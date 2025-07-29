# Instalando

poetry env use python
poetry env activate



poetry self add poetry-plugin-export
poetry export -f requirements.txt --output requirements.txt


python -m spacy download en_core_web_sm