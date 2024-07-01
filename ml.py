import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.dummy import DummyClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

np.random.seed(68)
train = pd.read_csv("train.csv")
xs_train = list(zip(train["hasText"].values,
                    train["maskedText"].values))
y_train = train["annotation"]
test = pd.read_csv("test.csv")
xs_test = list(zip(test["hasText"].values,
                    test["maskedText"].values))
y_test = test["annotation"]

dummy = DummyClassifier(strategy="stratified")
dummy.fit(xs_train[0], y_train)
print(classification_report(y_test, dummy.predict(xs_test[0])))

for x_train, x_test in zip(xs_train, xs_test):
    components = [('vectorizer', TfidfVectorizer(analyzer="word", ngram_range=(1,1), max_df=0.8)),
                  ('classifier', SVC(C=5))]
    pipe = Pipeline(components)
    pipe.fit(x_train, y_train)
    pred = pipe.predict(x_test)
    print(classification_report(y_test, pred))
#cm = pd.DataFrame(confusion_matrix(y_test, pred))
#cm.columns = pipe[-1].classes_
#cm.index = pipe[-1].classes_
#cm.to_csv("confusion.csv")
