import argparse
from pathlib import Path

from google.cloud import texttospeech
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

from constant import datadir


class VoiceGenerator:

    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()
        self.voice = texttospeech.VoiceSelectionParams(
            name="en-US-Neural2-C",
            language_code="en-US",
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

    def generate(self, text, word, index):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=self.voice, audio_config=self.audio_config
        )
        with open(Path(datadir) / f"{word}_{index:02d}.mp3", "wb") as out:
            out.write(response.audio_content)


class ChatManager:

    def __init__(self, n_sentences=4, n_words_lower=6, n_words_upper=10):
        self.llm = ChatOpenAI(temperature=0.9)
        self.n_sentences = n_sentences
        self.n_words_lower = n_words_lower
        self.n_words_upper = n_words_upper

    def make_english_examples(self, word):
        message = (
            f"Please make {self.n_sentences} sentences including the word \"{word}\"."
            f" The sentence should be consist of {self.n_words_lower} to {self.n_words_upper} words."
            " The output should be formatted as markdown with itemization."
        )
        ret = self.llm(
            [
                HumanMessage(content=message),
            ]
        )
        sentences = []
        for line in ret.content.split("\n"):
            line = line.rstrip()
            if len(line) == 0:
                continue
            if line[0].isalpha():
                continue
            line = line[1:].strip()
            sentences.append(line)

        return sentences

    def make_japanese_translation(self, eng_sentences, word):
        # いまいちなため未使用
        messages = [
            (
                "Please translate the following sentence in Japanese. The specified word must be replaced to ###. Do not output other than the Japanese translation.\n"
                "\n"
                f"Sentence: {eng_sentence}\n"
                f"Word to replace to ###: {word}"
            )
            for eng_sentence in eng_sentences
        ]
        ret = self.llm.generate(
            [
                [HumanMessage(content=message)]
                for message in messages
            ]
        )
        return [gen[0].text for gen in ret.generations]

    def evaluate_translation(self, eng_sentence, jp_sentence):
        message = (
            "以下の英文と日本語訳の対が翻訳として適切であるか、A:適切・B:中間・C:不適切の3段階で評価してください\n"
            "\n"
            "英文: {eng_sentence}"
            "日本語訳: {jp_sentence}"
        )

        ret = self.llm(
            [
                HumanMessage(content=message),
            ]
        )

        return ret.content


def main():
    parser = argparse.ArgumentParser(prog="Generate data from word list")
    parser.add_argument("--wordfile", default="wordlist.txt", help="Path to the word list file")
    parser.add_argument("--n_sentences", default=4, help="The number of examples to generate for each word")
    args = parser.parse_args()

    voice_generator = VoiceGenerator()
    chat_manager = ChatManager(args.n_sentences)

    with open(args.wordfile, "r") as f:
        for word in f.readlines():
            word = word.rstrip()
            if word == "":
                continue
            if (Path(datadir) / f"{word}_00.txt").exists():
                continue
            print(f"Generating examples: {word}")
            sentences = chat_manager.make_english_examples(word)
            # jps = chat_manager.make_japanese_translation(sentences, word)

            for i, sentence in enumerate(sentences):
                with open(Path(datadir) / f"{word}_{i:02d}.txt", "w") as f:
                    f.write(sentence)
                voice_generator.generate(sentence, word, i)


if __name__ == "__main__":
    main()
