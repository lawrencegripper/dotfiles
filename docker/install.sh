if test "$CODESPACES" = "true"
then
    echo "Skipping Docker config as in codespaces"
else
    echo "Start language tools spelling/grammer tool"
    docker start languagetool || docker run --name languagetool \
                            --cap-drop=ALL \
                            --user=65534:65534 \
                            --read-only \
                            --mount type=bind,src=/tmp,dst=/tmp \
                            --restart=always \
                            -p 8081:8010 \
                            -d \
                            silviof/docker-languagetool:latest@sha256:7337f7ec954e1e4302866c788ebf9049cf3a081ad069ab42a77a42d5dd996369
fi
