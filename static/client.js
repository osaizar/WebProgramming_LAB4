// TODO: Cambiar nombres de las funciones de diagramas
// TODO: Dividir en archivos distintos
// TODO: Despues de crear cuenta, borrar campos

//Costant declarations
const WELCOME = "welcomeview";
const PROFILE = "profileview";

var renderInterval;


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
        connectToWebSocket();
        renderCurrentUserPage();
    } else if (viewId == WELCOME) {
        bindFunctionsWelcome();
    }
};


window.onload = function() {
    displayView();
};

function getHMAC(data){
  var token = localStorage.getItem("token");
  if (token == null || token == "undefined"){
    return null;
  }else{
    var hmac_s = CryptoJS.HmacSHA256(btoa(data), token).toLocaleString();
    return CryptoJS.HmacSHA256(btoa(data), token).toLocaleString();
  }
}

// START request handlers

function sendHTTPRequest(data, url, method, onResponse){
    var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance
    var response = "";
    var request = {};
    var hmac_s = "";

    data["timestamp"] = parseInt(Date.now()/(1000*60*5)); // 5 minutes of margin
    request["data"] = JSON.stringify(data);

    hmac_s = getHMAC(JSON.stringify(data));
    if (hmac_s != null){
      request["hmac"] = hmac_s;
    }

    xmlhttp.open(method, url);
    xmlhttp.setRequestHeader("Content-Type", "application/json");
    xmlhttp.send(JSON.stringify(request));

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
      var jdata = {}
      var hmac_s = "";

      data["timestamp"] = parseInt(Date.now()/(1000*60*5)); // 5 minutes of margin

      jdata["data"] = JSON.stringify(data);
      hmac_s = getHMAC(JSON.stringify(data));
      if (hmac_s != null){
        jdata["hmac"] = hmac_s;
      }

      socket.send(JSON.stringify(jdata));
      socket.onmessage = function(s){
        response = JSON.parse(s.data);
        if (!response.success){
          handleSocketMessage(response.message)
        }else{
          onRespose(response);
        }
      };
    }, socket);
}


function handleSocketMessage(message) {
  switch (message) {
    case "close:session":
      signOut();
      break;
    case "You are not loged in!":
      signOut();
      break;
    case "reload:messages":
      reloadMessages();
      break;
    case "reload:connected":
      renderConnectedUserDiagram();
      break;
    case "reload:log":
      renderUserHistoryDiagram();
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
  var data = {"email": localStorage.getItem("email")};
  sendToWebSocket(data, "/connect", function(server_msg){
    if(!server_msg.success){
      signOut();
    }
  });
}

// END request handlers


// START diagrams

function renderDiagrams() {
  renderConnectedUserDiagram();
  renderUserHistoryDiagram();
  reloadMessages();
  // message diagram gets loaded with the messagess
}

function renderConnectedUserDiagram(){
  var data = {"email": localStorage.getItem("email")};
  sendToWebSocket(data, "/get_current_conn_users", function(server_msg){
  var jdata = {};
  var fields = [];

  fields.push("Connected Users");
  fields.push("Not Connected Users");
  jdata["Not Connected Users"] = server_msg.data.totalUsers-server_msg.data.connectedUsers;
  jdata["Connected Users"] = server_msg.data.connectedUsers;

  var diagram1 = c3.generate({
    bindto: '#diagram0',
    data: {
        json: [ jdata ],
        keys: {
          value: fields,
        },
        type:'donut'
      },
      donut: {
        title: "Total Users: "+server_msg.data.totalUsers
      }
    });
  });
}


function renderUserHistoryDiagram(){
  var data = {"email": localStorage.getItem("email")};
  sendToWebSocket(data, "/get_conn_user_history", function(server_msg){

      var x = [];
      var data = [];
      var i = 0;
      x[0] = "Hour";
      data[0] = "Connected users";

      var arr = Object.keys(server_msg.data).map(function(k) { return server_msg.data[k] });

      for(var i = 0; i < arr.length; i++){
        x[i+1] = i+":00";
        data[i+1] = arr[i];
      }

      var chart = c3.generate({
        bindto: '#diagram1',
        data: {
            x: 'Hour',
            xFormat: '%H:%M',
            columns: [
              x,
              data,
            ]
        },
        axis: {
            x: {
                type: 'timeseries',
                tick: {
                    format: '%H:%M'
                }
            }
        }
      });
    });
}

function renderCommentDiagram(messages){
  var jdata = {};
  var fields = [];

  if (messages != ""){
    for (var i = 0; i < messages.length; i++) {
      var writer = messages[i].writer;
      if (fields.indexOf(writer) == -1){
        fields.push(writer);
        jdata[writer] = 1;
      }else{
        jdata[writer] = jdata[writer]+1;
      }
    }

    var diagram1 = c3.generate({
      bindto: '#diagram2',
      data: {
          json: [ jdata ],
          keys: {
            value: fields,
          },
          type:'pie'
        },
    });
  }else{
    var diagram = document.getElementById("diagram2");
    var h4 = document.createElement("h4");
    h4.innerHTML = "You have no messages";
    diagram.innerHTML = "";
    diagram.appendChild(h4);
  }
}

// END diagrams


// START client side functions

function signIn() {

    var email = document.forms["loginForm"]["lemail"].value;
    var password = document.forms["loginForm"]["lpassword"].value;

    var data = {"email":email, "password":password};
    sendHTTPRequest(data, "/sign_in", "POST", function(server_msg){
      if (!server_msg.success) {
          showSignInError(server_msg.message);
      } else {
          document.forms["loginForm"].reset();
          localStorage.setItem("token", server_msg.data.token);
          localStorage.setItem("email", server_msg.data.email);
          displayView();
      }
    });
    return false;
}

function showSignInError(message) { // se usa en sigUp y signIn
    document.getElementById("messageSignInErr").innerHTML = message;
    document.getElementById("signInError").style.display = "block";
    //document.getElementById("signInSucc").style.display = "none"; da error
}

function showSignInSuccess(message) { // se usa en sigUp y signIn
    document.getElementById("messageSignInSucc").innerHTML = message;
    document.getElementById("signInSuccess").style.display = "block";
    document.getElementById("signInError").style.display = "none";
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
    var email = document.forms["signupForm"]["semail"].value;
    var password = document.forms["signupForm"]["spassword"].value;

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
        document.forms["signupForm"].reset();
        showSignUpSuccess(server_msg.message)
      }
    });
    return false;
}


function signOut() {

    var email = localStorage.getItem("email");
    sendHTTPRequest({"email":email}, "/sign_out", "POST", function(server_msg){
      if(!server_msg.success){
        showChangePasswordError(server_msg.message);
      }
      localStorage.setItem("token", "undefined"); // TODO: Mirad esto plis
      localStorage.setItem("email", "undefined");
      displayView();
    });
}


function openUserTab() {

    document.getElementById("userPage").style.display = "block";

}


function changePassword() {

    var npassword = document.forms["changePassForm"]["new_password"].value;
    var cpassword = document.forms["changePassForm"]["current_password"].value;
    var email = localStorage.getItem("email");
    var data = {"email":email, "old_password": cpassword, "new_password": npassword};
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

    var email = localStorage.getItem("email");
    var data = {"email":email};
    sendHTTPRequest(data, "/get_user_data", "POST", function(server_msg) {
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

      reloadMessages();
    });
}


function sendMessage() {

    var email = localStorage.getItem("email");
    sendHTTPRequest({"email":email}, "/get_user_data", "POST", function(server_msg){
      var data;

      if (server_msg.success) {
          data = server_msg.data;
      } else {
          return -1; //error
      }

      var msg = document.forms["msgForm"]["message"].value;

      document.forms["msgForm"]["message"].value = "";

      var server_msg = sendHTTPRequest({"email":email, "msg":msg,"reader": data.email}, "/send_message", "POST", function (server_msg) {
        reloadMessages();
        document.getElementById("msgToMe").value = "";
      });
    });
    return false;
}


function sendMessageTo() {

    var email = localStorage.getItem("email");
    var reader = document.getElementById("othEmailField").innerHTML;
    var msg = document.forms["msgToForm"]["message"].value;

    sendHTTPRequest({"email":email, "msg":msg, "reader": reader}, "/send_message", "POST", function(server_msg){
      reloadOtherUserMessages();
      document.getElementById("msgTo").value = "";
    });
    return false;
}


function reloadMessages() {

    var email = localStorage.getItem("email");
    sendHTTPRequest({"email":email}, "/get_user_messages", "POST", function(server_msg) {
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
          var b = document.createElement('b');
          var span = document.createElement('span');
          b.setAttribute("id","msgContent"+i);
          b.innerHTML = messages[i].content;
          span.setAttribute("id","msgWriter"+i);
          span.innerHTML = " by " + messages[i].writer;
          p.appendChild(b);
          p.appendChild(span);
          p.setAttribute("draggable","true");
          p.setAttribute("ondragstart","drag(event)");
          p.setAttribute("id","message"+i);
          //p.innerHTML = messages[i].content + " by " + messages[i].writer;

          msgDiv.appendChild(p);
      }

      renderCommentDiagram(messages);
    });
}


function reloadOtherUserMessages() {

    var email = localStorage.getItem("email");
    var userEmail = document.getElementById("othEmailField").innerHTML;
    sendHTTPRequest({"email":email, "userEmail":userEmail}, "/get_user_messages_by_email", "POST", function(server_msg){
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
          var b = document.createElement('b');
          var span = document.createElement('span');
          b.setAttribute("id","msgContent"+i);
          b.innerHTML = messages[i].content;
          span.setAttribute("id","msgWriter"+i);
          span.innerHTML = " by " + messages[i].writer;
          p.appendChild(b);
          p.appendChild(span);
          p.setAttribute("draggable","true");
          p.setAttribute("ondragstart","drag(event)");
          p.setAttribute("id","message"+i);
          //p.innerHTML = messages[i].content + " by " + messages[i].writer;

          msgDiv.appendChild(p);
      }
    });
}


function searchUser() {

    var email = localStorage.getItem("email");
    var userEmail = document.forms["userSearchForm"]["email"].value;
    sendHTTPRequest({"email":email,"userEmail":userEmail}, "/get_user_data_by_email", "POST", function(server_msg){
      var userData;

      if (!server_msg.success) {
          showSearchError(server_msg.message);
      } else {
          userData = server_msg.data;
          renderOtherUserPage(userData);
          openUserTab();
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

    reloadOtherUserMessages();
}


function allowDrop(ev) {
    ev.preventDefault();
}


function drag(ev) {
    var img = document.createElement("img");
    img.src = "dragImage.png";
    img.style.height = "10px";
    ev.dataTransfer.setDragImage(img, 0, 0);
    var message = ev.target;
    var messageID = message.id;
    messageID = messageID.replace("message", "");

    var content = document.getElementById("msgContent"+messageID).innerHTML;
    var writer = document.getElementById("msgWriter"+messageID).innerHTML;
    var dragMessage = "\"" + content + "\"" + writer;
    ev.dataTransfer.setData("text", dragMessage);
    //ev.dataTransfer.setData("text", ev.target.innerHTML);
}


function drop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");
    //var p = document.createElement('p');
    //p.innerHTML = "Response for" + data + ": ";
    ev.target.appendChild(data);
}

// END client side functions


function bindFunctionsWelcome() {

    document.getElementById("loginForm").onsubmit = signIn;
    document.getElementById("signupForm").onsubmit = signUp;

    document.getElementById("s_rpassword").onkeyup = checkPasswords;
}


function bindFunctionsProfile() {
    document.getElementById("navAccount").onclick = renderDiagrams;
    document.getElementById("logout").onclick = signOut;
    document.getElementById("msgForm").onsubmit = sendMessage;
    document.getElementById("msgToForm").onsubmit = sendMessageTo;
    document.getElementById("userSearchForm").onsubmit = searchUser;
    document.getElementById("changePassForm").onsubmit = changePassword;
    document.getElementById("s_rpassword").onkeyup = checkPasswords;
}
