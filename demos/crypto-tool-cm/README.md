# Crypto tool for CipherTrust Manager

![image](https://user-images.githubusercontent.com/111074839/207679307-1f62783f-9ef8-4e58-ba8e-9e168e78371f.png)

## For Ubuntu 20.04 host

### Install Node.js and npm first
```
sudo apt update
sudo apt install nodejs
sudo apt install npm
```
### Deploy this software
Clone this repo
```
git clone https://github.com/thalescpl-io/CipherTrust_Application_Protection.git
```
Install and run the application
```
cd demos/cm-crypto-tool
npm install
npm run dev
```
### Open the web interface on your favorite browser (tested on Chrome only)
```
http://server:3000/
```

## Using the tool

### Create session first
Session is a JWT based authenticated session that this crypto tool would need to interact with CipherTrust Manager's APIs
Session requires user to input the CipherTrust Manager server address and username/password based crdentials (other auth methods are not supported yet)
<kbd><img src="https://user-images.githubusercontent.com/111074839/207629672-3ffdc04c-9147-4748-81d9-849fa719dbb0.png" /></kbd>

### Manually refresh token
A JWT will remain valid for 5 minutes, so you might have to manually refresh token from the sessions page
<kbd><img src="https://user-images.githubusercontent.com/111074839/207635504-489e7e82-a39f-4bfa-8414-43ad4e8c825e.png" /></kbd>

### Perform the desired crypto operation by selecting the session and corresponding key
<kbd><img src="https://user-images.githubusercontent.com/111074839/207630292-b21373a8-3c9c-4ae8-aed3-d49142ca3b96.png" /></kbd>
