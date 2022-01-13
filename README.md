# finding-handles

## Dependencies
- python3
- requests
- regex
- json
- sys
- logging
- bs4 (beautifulsoup)
- datetime

This python script takes urls from a local text file and parses through them with beautifulsoup to find all instances of Twitter handles, Facebook page ids, iOS app store ids, and Google Play Store ids. It returns them in a local json file in the following structure:
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
