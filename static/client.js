//Costant declarations
const WELCOME = "welcomeview";
const PROFILE = "profileview";


displayView = function() {
    var viewId;
    if (localStorage.getItem("token") == "undefined" || localStorage.getItem("token") == null) {
        viewId = WELCOME;
    } else {
        viewId = PROFILE;
    }
    document.getElementById("innerDiv").innerHTML = document.getElementById(viewId).innerHTML;
    if (viewId == PROFILE) {
        bindFunctionsProfile();
        openTab("menu", "home");
        connectToWebSocket();
    } else if (viewId == WELCOME) {
        bindFunctionsWelcome();
    }
};


window.onload = function() {
    displayView();
};

function sendHTTPRequest(data, url, method, onResponse){
    var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance
    var response = "";

    xmlhttp.open(method, url);
    xmlhttp.setRequestHeader("Content-Type", "application/json");
    xmlhttp.send(JSON.stringify(data));

    xmlhttp.onreadystatechange = function(){
      if (this.readyState == 4 && this.status == 200){
        response = xmlhttp.responseText;
        onResponse(JSON.parse(response));
      }
    }
}

function sendToWebSocket(data, url, onRespose){
    var socket = new WebSocket("ws://localhost:8080"+url); //localhost ??
    waitForConnection(function(){
      socket.send(JSON.stringify(data));
      socket.onmessage = function(s){
        response = JSON.parse(s.data);
        if (!response.success){
          handleSocketError(response.message)
        }else{
          onRespose(response);
        }
        onRespose(response);
      };
    }, socket);
}

function handleSocketError(message) {
  switch (message) {
    case "close:session":
      signOut();
      break;
    case "You are not loged in!":
      signOut();
      break;
    default:
      break;
  }
}

function waitForConnection(callback, socket){
  if(socket.readyState == 1){
    callback();
  }else{
    setTimeout(function(){
      waitForConnection(callback, socket);
    }, 1000);
  }
}

function connectToWebSocket(){
  var data = {"token": localStorage.getItem("token")};
  sendToWebSocket(data, "/connect", function(server_msg){
    if(!server_msg.success){
      signOut();
    }
  });
}

function signIn() {

    var email = document.forms["loginForm"]["email"].value;
    var password = document.forms["loginForm"]["password"].value;

    var data = {"email":email, "password":password};
    sendHTTPRequest(data, "/sign_in", "POST", function(server_msg){
      if (!server_msg.success) {
          showSignUpError(server_msg.message);
      } else {
          localStorage.setItem("token", server_msg.data.token);
          displayView();
      }
    });
    return false;
}


function showSignUpError(message) { // se usa en sigUp y signIn
    document.getElementById("messageSignUpErr").innerHTML = message;
    document.getElementById("signUpError").style.display = "block";
    document.getElementById("signUpSuccess").style.display = "none";
}

function showSignUpSuccess(message) { // se usa en sigUp y signIn
    document.getElementById("messageSignUpSucc").innerHTML = message;
    document.getElementById("signUpSuccess").style.display = "block";
    document.getElementById("signUpError").style.display = "none";
}


function checkPasswords(type) {

    var password = document.getElementById("s_password");
    var rpassword = document.getElementById("s_rpassword");

    if (password.value != rpassword.value) {
        rpassword.setCustomValidity("Passwords do not match!");
    } else {
        rpassword.setCustomValidity('');
    }
}


function signUp() {

    var firstname = document.forms["signupForm"]["name"].value;
    var familyname = document.forms["signupForm"]["f-name"].value;
    var gender_select = document.getElementById("gender");
    var gender = gender_select.options[gender_select.selectedIndex].text;
    var city = document.forms["signupForm"]["city"].value;
    var country = document.forms["signupForm"]["country"].value;
    var email = document.forms["signupForm"]["email"].value;
    var password = document.forms["signupForm"]["password"].value;

    var user = {
        "email": email,
        "password": password,
        "firstname": firstname,
        "familyname": familyname,
        "gender": gender,
        "city": city,
        "country": country
    };

    sendHTTPRequest(user, "/sign_up", "POST", function(server_msg){
      if (!server_msg.success) {
          showSignUpError(server_msg.message);
      }else{
        showSignUpSuccess(server_msg.message)
      }
    });
    return false;
}


function signOut() {

    var token = localStorage.getItem("token");
    sendHTTPRequest({"token":token}, "/sign_out", "POST", function(server_msg){
      if(!server_msg.success){
        showChangePasswordError(server_msg.message);
      }
      localStorage.setItem("token", "undefined"); // TODO: Mirad esto plis
      displayView();
    });
}

function openTab(tabType, tabName) {

    var i;
    var tabId;
    var menu = document.getElementsByClassName(tabType);
    var tabLinks = document.getElementsByClassName("tabLink");

    if (tabType == "menu") {
        if (tabName == "home") {
            tabId = "navHome";
        }
        if (tabName == "browse") {
            tabId = "navBrowse";
        }
        if (tabName == "account") {
            tabId = "navAccount";
        }

        for (i = 0; i < menu.length; i++) {
            tabLinks[i].className = tabLinks[i].className.replace(" active", "");
        }

        document.getElementById(tabId).className += " active";
    }


    for (i = 0; i < menu.length; i++) {
        menu[i].style.display = "none";
    }

    document.getElementById(tabName).style.display = "block";


    if (tabName == "home") {
        renderCurrentUserPage();
    }

}


function changePassword() {

    var npassword = document.forms["changePassForm"]["new_password"].value;
    var cpassword = document.forms["changePassForm"]["current_password"].value;
    var token = localStorage.getItem("token");
    var data = {"token":token, "old_password": cpassword, "new_password": npassword};
    sendHTTPRequest(data, "/change_password", "POST", function(server_msg){
      if (!server_msg.success) {
          showChangePasswordError(server_msg.message);
      } else {
          showChangePasswordSuccess(server_msg.message);
      }
    });
    return false;
}

function showChangePasswordError(message) { // se usa en signOut tambien
    document.getElementById("messageChPassword").innerHTML = message;
    document.getElementById("chPasswordError").style.display = "block";

    document.getElementById("chPasswordSuccess").style.display = "none";
}

function showChangePasswordSuccess(message) {
    document.getElementById("messageChPasswordS").innerHTML = message;
    document.getElementById("chPasswordSuccess").style.display = "block";

    document.getElementById("chPasswordError").style.display = "none";
}


function renderCurrentUserPage() {

    var token = localStorage.getItem("token");
    var data = {"token":token};
    sendHTTPRequest(data, "/get_user_data_by_token", "POST", function(server_msg) {
      var userData;

      if (server_msg.success) {
          userData = server_msg.data;
      } else {
          return -1; //error
      }

      document.getElementById("nameField").innerHTML = userData.firstname;
      document.getElementById("fNameField").innerHTML = userData.familyname;
      document.getElementById("genderField").innerHTML = userData.gender;
      document.getElementById("countryField").innerHTML = userData.country;
      document.getElementById("cityField").innerHTML = userData.city;
      document.getElementById("emailField").innerHTML = userData.email;

      reloadUserMessages();
    });
}


function sendMessage() {

    var token = localStorage.getItem("token");
    sendHTTPRequest({"token":token}, "/get_user_data_by_token", "POST", function(server_msg){
      var data;

      if (server_msg.success) {
          data = server_msg.data;
      } else {
          return -1; //error
      }

      var msg = document.forms["msgForm"]["message"].value;

      document.forms["msgForm"]["message"].value = "";

      var server_msg = sendHTTPRequest({"token":token, "msg":msg,"reader": data.email}, "/send_message", "POST");

      reloadUserMessages();

      document.getElementById("msgToMe").value = "";
    });
    return false;
}


function sendMessageTo() {

    var token = localStorage.getItem("token");
    var email = document.forms["userSearchForm"]["email"].value;
    var msg = document.forms["msgToForm"]["message"].value;

    sendHTTPRequest({"token":token, "msg":msg,"reader": email}, "/send_message", "POST", function(server_msg){
      reloadMessages();
      document.getElementById("msgTo").value = "";
    });
    return false;
}


function reloadUserMessages() {

    var token = localStorage.getItem("token");
    sendHTTPRequest({"token":token}, "/get_user_messages_by_token", "POST", function(server_msg) {
      var messages;

      if (server_msg.success) {
          messages = server_msg.data;
      } else {
          return -1; //error
      }

      var msgDiv = document.getElementById("userMessageDiv");

      while (msgDiv.firstChild) {
          msgDiv.removeChild(msgDiv.firstChild);
      }

      for (var i = 0; i < messages.length; i++) {
          var p = document.createElement('p');
          p.innerHTML = "<b>" + messages[i].content + "</b> by " + messages[i].writer;
          msgDiv.appendChild(p);
      }
    });
}


function reloadMessages() {

    var token = localStorage.getItem("token");
    var email = document.forms["userSearchForm"]["email"].value;
    sendHTTPRequest({"token":token, "email":email}, "/get_user_messages_by_email", "POST", function(server_msg){
      var messages;

      if (server_msg.success) {
          messages = server_msg.data;
      } else {
          return -1; //error
      }

      var msgDiv = document.getElementById("messageDiv");

      while (msgDiv.firstChild) {
          msgDiv.removeChild(msgDiv.firstChild);
      }

      for (var i = 0; i < messages.length; i++) {
          var p = document.createElement('p');
          p.innerHTML = "<b>" + messages[i].content + "</b> by " + messages[i].writer;
          msgDiv.appendChild(p);
      }
    });
}


function searchUser() {

    var token = localStorage.getItem("token");
    var email = document.forms["userSearchForm"]["email"].value;
    sendHTTPRequest({"token":token,"email":email}, "/get_user_data_by_email", "POST", function(server_msg){
      var userData;

      if (!server_msg.success) {
          showSearchError(server_msg.message);
      } else {
          userData = server_msg.data;
          renderOtherUserPage(userData);
          openTab("browsetab", "user");
      }
    });
    return false;
}

function showSearchError(message) {
    document.getElementById("messageSearch").innerHTML = message;
    document.getElementById("searchError").style.display = "block";
}




function renderOtherUserPage(userData) {

    document.getElementById("othNameField").innerHTML = userData.firstname;
    document.getElementById("othFNameField").innerHTML = userData.familyname;
    document.getElementById("othCountryField").innerHTML = userData.gender;
    document.getElementById("othCityField").innerHTML = userData.country;
    document.getElementById("othGenderField").innerHTML = userData.city;
    document.getElementById("othEmailField").innerHTML = userData.email;

    reloadMessages();
}


function back() {
    openTab("browsetab", "search");
}


function bindFunctionsWelcome() {

    document.getElementById("loginForm").onsubmit = signIn;
    document.getElementById("signupForm").onsubmit = signUp;

    document.getElementById("s_rpassword").onkeyup = checkPasswords;
}


function bindFunctionsProfile() {

    document.getElementById("navHome").onclick = function() {
        openTab("menu", "home");
    };
    document.getElementById("navBrowse").onclick = function() {
        openTab("menu", "browse");
    };
    document.getElementById("navAccount").onclick = function() {
        openTab("menu", "account");
    };

    document.getElementById("userMsgReloadButton").onclick = reloadUserMessages;
    document.getElementById("logout").onclick = signOut;
    document.getElementById("back").onclick = back;
    document.getElementById("msgReloadButton").onclick = reloadMessages;

    document.getElementById("msgForm").onsubmit = sendMessage;
    document.getElementById("msgToForm").onsubmit = sendMessageTo;
    document.getElementById("userSearchForm").onsubmit = searchUser;
    document.getElementById("changePassForm").onsubmit = changePassword;

    document.getElementById("s_rpassword").onkeyup = checkPasswords;
}
