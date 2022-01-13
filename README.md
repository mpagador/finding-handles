# finding-handles
 
This python script takes urls from a text file and parses through them with beautifulsoup to find all instances of Twitter handles, Facebook page ids, iOS app store ids, and Google Play Store ids. It returns them as a json string in the following structure:
```json
{
    "https://www.firsturl.com": {
        "twitter": "twitterhandle",
        "facebook": "facebookhandle",
        "ios": "00000000"
        "google": "com.example"
    },
    "https://www.secondurl.com": {
        "twitter": "twitterhandle",
        "facebook": "facebookhandle",
        "ios": "00000000"
        "google": "com.example"
    }
}
```
