# 英単語リスニング用

## Setup

#### Verified
* Windows WSL2, Ubuntu 20.04
* Python >= 3.10

#### Requirements
* OpenAI API
* Google Cloud

OPEN AI Key

```bash
export OPENAI_API_KEY=`cat /path/to/openai_api_key.txt`
```

Google Cloud

```bash
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-435.0.1-linux-x86_64.tar.gz
gcloud auth application-default login
gcloud components update
gcloud auth application-default set-quota-project "<id-of-project>"
```

VLC

```bash
sudo apt install vlc
```

Python

```bash
pip3 install -r requirements.txt
```

## Launch

```bash
python3 run.py
```
