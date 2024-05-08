FROM ollama/ollama

# Указываем директорию для сохранения моделей
VOLUME ["/root/.ollama"]

RUN bash -c '                                  \
    ( ollama serve ) & serverpid="$!";         \
    sleep 5;                                   \
    ollama pull starling-lm  &&      \
    kill "$serverpid" &&                       \
    wait "$serverpid"                          \
'
EXPOSE 11434