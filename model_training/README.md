# TAPMODELV2_BERT TRAINING

Here there are .ipynb sheets with TapModelv2_BERT model training. 

The part 1 sheet contains dataset preprocessing. Part 2 contains the effective training attempts:
1. Apache Spark MLLib Logistic Regression;
2. scikit-learn SVM with non-linear kernel;
3. roBERTa-base model directly from HF, fine-tuned using Pytorch library.

Final model is based on original BERT-base model (this attempt isn't in .ipynb sheet), given that performances are the same as roBERTa-base.

  
