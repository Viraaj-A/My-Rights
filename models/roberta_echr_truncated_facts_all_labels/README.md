---
license: mit
base_model: roberta-base
tags:
- generated_from_trainer
metrics:
- f1
- accuracy
model-index:
- name: roberta_echr_truncated_facts_all_labels
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# roberta_echr_truncated_facts_all_labels

This model is a fine-tuned version of [roberta-base](https://huggingface.co/roberta-base) on an unknown dataset.
It achieves the following results on the evaluation set:
- Loss: 0.0674
- F1: 0.7452
- Roc Auc: 0.8460
- Accuracy: 0.5883

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 2e-05
- train_batch_size: 8
- eval_batch_size: 8
- seed: 42
- optimizer: Adam with betas=(0.9,0.999) and epsilon=1e-08
- lr_scheduler_type: linear
- num_epochs: 5

### Training results

| Training Loss | Epoch | Step | Validation Loss | F1     | Roc Auc | Accuracy |
|:-------------:|:-----:|:----:|:---------------:|:------:|:-------:|:--------:|
| 0.0835        | 1.0   | 1765 | 0.0780          | 0.6933 | 0.7942  | 0.5214   |
| 0.0674        | 2.0   | 3530 | 0.0699          | 0.7375 | 0.8363  | 0.5577   |
| 0.0584        | 3.0   | 5295 | 0.0674          | 0.7452 | 0.8460  | 0.5883   |
| 0.0474        | 4.0   | 7060 | 0.0690          | 0.7372 | 0.8448  | 0.5787   |
| 0.04          | 5.0   | 8825 | 0.0695          | 0.7429 | 0.8475  | 0.5870   |


### Framework versions

- Transformers 4.35.2
- Pytorch 2.1.1+cu121
- Datasets 2.14.5
- Tokenizers 0.15.1
