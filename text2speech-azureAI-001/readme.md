# text 2 speech

## setup

``` python
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## run

- save to file

`python main.py "my_word" --key abc123def456 --region eastus --output my_word.wav`

- play the text

`python main.py "artificial intelligence" --key abc123def456 --region eastus --play`
