import nltk

from .spam import NB

nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("wordnet")
nltk.download("omw-1.4")
nltk.download("averaged_perceptron_tagger_eng")


dataset_train = [
    # --- SPAM SAMPLES ---
    ("send us your password immediately", "spam"),
    ("review our website for rewards", "spam"),
    ("send your password to verify account", "spam"),
    ("send us your account details now", "spam"),
    ("free luxury watch for our customers", "spam"),
    ("win a free gift card today", "spam"),
    ("urgent: your account password has expired", "spam"),
    ("click here to review your prize", "spam"),
    ("your bank account needs verification", "spam"),
    ("claims your rewards on our website", "spam"),
    ("exclusive offer for website members", "spam"),
    ("get cheap insurance quotes now", "spam"),
    # --- HAM SAMPLES ---
    ("Your weekly activity report is ready", "ham"),
    ("the benefits of physical activity are many", "ham"),
    ("understanding the importance of wedding vows", "ham"),
    ("meeting scheduled for next Tuesday", "ham"),
    ("please review the attached report", "ham"),
    ("vows are a key part of the ceremony", "ham"),
    ("your activity on the account was normal", "ham"),
    ("the importance of maintaining a healthy website", "ham"),
    ("physical activity reduces stress levels", "ham"),
    ("thank you for the birthday wishes", "ham"),
    ("can you send me the password for the wifi", "ham"),
    ("the benefits of a diverse team", "ham"),
]

dataset_test = [
    # Expected: Spam (Keywords: renew, password, urgent)
    ("renew your password urgently", "spam"),
    # Expected: Spam (Keywords: rewards, website)
    ("get rewards from our website", "spam"),
    # Expected: Ham (Keywords: benefits, account - but in a non-urgent context)
    ("discuss the benefits of our account", "ham"),
    # Expected: Ham (Keywords: importance, physical, activity)
    ("the importance of daily physical activity", "ham"),
    # Expected: Ham (Testing "vows" in ham context)
    ("writing your own wedding vows", "ham"),
    # Expected: Spam (Testing "free" and "win")
    ("win a free luxury watch", "spam"),
]

#print(f"{dataset_train}")
#print(f"{dataset_test}")

classifier = NB(k=1, m=2)
classifier.train(dataset_train)

print("\nTop Spam Words:")
print(classifier.get_spam_vocab(5))

correct = 0
print("\n--- Testing Phase ---")
for text, label in dataset_test:
    prediction, prob = classifier.predict(text)
    is_correct = prediction == label
    if is_correct:
        correct += 1

    print(f"Text: '{text}'")
    print(f"Actual: {label} | Predicted: {prediction} (Prob: {prob:.4f})")
    print("-" * 20)

accuracy = (correct / len(dataset_test)) * 100
print(f"\nFinal Accuracy: {accuracy:.2f}%")
