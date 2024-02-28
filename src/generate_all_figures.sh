for aspect in helpfulness quantity relevance repetitiveness clarity ambiguity; do
    python draw.py \
        --input-path ../data/conversation_raw.xlsx\
        --output-path ../output/${aspect}.png\
        --aspect ${aspect}
done