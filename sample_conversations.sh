#!/bin/bash

INPUT_TREES_DIR="data/trees_jsonl"
OUT_DIR="data/conversations"

PERCENTAGE_OF_LEAVES_TO_SAMPLE=1.0
MIN_LEN=30  # in number of chars / conversation
MAX_REPEAT_OF_NODE=3
VAL_PER_SCORE=1
VAL_PER_CHAR=0.05
VAL_PER_DESCENDANT=0.2
VAL_SUB_PER_VISIT=10


python3 tree_to_conversations/sample_from_trees.py \
    --in_dir $INPUT_TREES_DIR \
    --out_dir $OUT_DIR \
    --percentage_of_leaves $PERCENTAGE_OF_LEAVES_TO_SAMPLE \
    --min_len $MIN_LEN \
    --max_repeat $MAX_REPEAT_OF_NODE \
    --val_per_score $VAL_PER_SCORE \
    --val_per_char $VAL_PER_CHAR \
    --val_per_desc $VAL_PER_DESCENDANT \
    --val_sub_per_visit $VAL_SUB_PER_VISIT
