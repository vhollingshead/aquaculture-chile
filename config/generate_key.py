import pickle
from pathlib import Path
import streamlit_authenticator as stauth


names = ["aquaculture chile app", "Mihir Bhaksi", "Danny", "Evan", "Victoria", "Elena", "Pablo"]
usernames = ["aquaculture-chile-app", "mihir", "danny", "evan", "victoria", "elena", "pablo"]
passwords = ["XXX", "XXX", "XXX", "XXX", "XXX", "XXX", "XXX"]

hashed_passwords = stauth.Hasher(passwords).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"

with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)