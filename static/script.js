
const server = "http://localhost:8080"
let username

async function sendRequest(url, method, data){
    try {
    let token = window.localStorage.getItem('access_token')

    let options = {
        "method" : method,
        "headers" : {
        "Content-Type" : "application/json",
        "Authorization" : `JWT ${token}`
        }
    }

    if(data)
        options.body = JSON.stringify(data)

        let response = await fetch(url, options)

        let result = await response.json()

        return result
    } catch (e) {
        console.log(e)
    }
}

async function login(event){
    event.preventDefault();

    let form = event.target
    let fields = event.target.elements

    let data = {
    "username" : fields["username"].value,
    "password" : fields["password"].value,
    }

    form.reset()

    let result = await sendRequest(`${server}/auth`, "POST", data)

    if("error" in result) {
        updateModalContent("Login", `Login failed! ${result["error"]}.`)
    } else {
        console.log("Logged in successfully!")
        updateModalContent("Login", `Login successful!`)

        window.localStorage.setItem('access_token', result['access_token']);
    } 
    determineSessionContext()
    $('#loginModal').modal('hide')
}

async function signUp(event){
    event.preventDefault();

    let form = event.target
    let fields = event.target.elements

    let data = {
    "username" : fields["regUsername"].value,
    "firstName" : fields["firstName"].value,
    "lastName" : fields["lastName"].value,
    "password" : fields["regPassword"].value,
    "confirmPassword" : fields["confirmPassword"].value
    }

    console.log(data)

    form.reset()

    let result = await sendRequest(`${server}/register`, "POST", data)

    if("error" in result) {
        console.log("Sign up failed! " + result["error"])
        updateModalContent("Electora Registration", `Sign up failed! ${result["error"]}.`)
    } else {
        updateModalContent("Electora Registration", `${result["message"]}.`)
        console.log("Signed up successfully!")
    }
    $('#signUpModal').modal('hide')
}

function updateModalContent(newModalTitle, newModalContent){
    let modalTitle = document.querySelector("#genericModalTitle")
    let modalBody = document.querySelector("#genericModalMessage")

    modalTitle.innerHTML = newModalTitle
    modalBody.innerHTML = newModalContent
    $('.toast').toast("show")
}

function logout(){
    console.log("test")
    accessToken = window.localStorage.getItem("access_token");
    if(accessToken){
        window.localStorage.removeItem('access_token');
        updateModalContent("Logout", "Succesfully logged out!")
    } else {
        updateModalContent("Logout", "You were not logged in!")
    }
    determineSessionContext()
}

async function determineSessionContext(){
    let token = window.localStorage.getItem("access_token")
    let logoutButton = document.querySelector("#logoutButton")
    
    if(token){
        username = await sendRequest(`${server}/identify`, "GET")
        logoutButton.innerText = "Logout"
        navbarLinks.innerHTML = `
                                <li class="nav-item">
                                    <a class="nav-link" href="#">Logged in as ${username.username}!</a>
                                </li>`
    } else {
        logoutButton.innerText = ""
        navbarLinks.innerHTML = `<li class="nav-item">
                                    <a class="nav-link" id="navLink1" href="#" data-toggle="modal" data-target="#loginModal">Login</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" id="navLink2" href="#" data-toggle="modal" data-target="#signUpModal">Register</a>
                                </li>`
    }
    
}

async function displayClubs(clubs){
    clubArea = document.querySelector("#clubDisplayArea")
    let listOfClubs = ""
    if(clubs.length > 0){
        
        for(club of clubs){
            listOfClubs += `<div class="col-sm-6 mt-3">
                              <div class="card" style="width: 100%;">
                                <img class="card-img-top" src="${club["clubImage"]}" alt="Card image cap">
                                <div class="card-body">
                                  <h5 class="card-title">${club["clubName"]}</h5>
                                  <p class="card-text">${club["clubDescription"]}</p>
                                  <a href="#" onclick="joinClub(${club["clubID"]})" class="btn btn-primary">Join Club</a>
                                </div>
                              </div>
                            </div> `
        }
        
        clubDisplayArea.innerHTML = listOfClubs
        
    } else {
        console.log("No clubs")
    }
}


async function getAllClubs(){
    let clubs = await sendRequest(`${server}/api/clubs`, "GET")
    displayClubs(clubs)
}


async function displayMyClubs(myClubs){
    console.log(myClubs)
    myClubsArea = document.querySelector("#myClubsDisplayArea")
    let listOfClubs = ""
    if(myClubs.length > 0){
        for(myClub of myClubs){
            listOfClubs += `<div class="col-sm-6 mt-3">
                              <div class="card" style="width: 100%;">
                                <img class="card-img-top" src="${myClub["clubImage"]}" alt="Card image cap">
                                <div class="card-body">
                                  <h5 class="card-title">${myClub["clubName"]}</h5>
                                  <p class="card-text">${myClub["clubDescription"]}</p>
                                  <a href="#" onclick="leaveClub(${myClub["clubID"]})" class="btn btn-danger">Leave club</a>
                                </div>
                              </div>
                            </div> `
        }
        
        myClubsArea.innerHTML = listOfClubs
    } else {
        console.log("No clubs")
        
        myClubsArea.innerHTML = 
        `<div class="col-sm-12 mt-3 text-center"">
            <h5>No Joined Clubs</h5>
            <p>Sorry, but you are not a member of any clubs. You can join a club via the 'Clubs' tab.</p>
        </div> `
    }

}

async function getAllMyClubs(){
    let myClubs = await sendRequest(`${server}/api/myClubs`, "GET")
    displayMyClubs(myClubs)
}

async function joinClub(clubID){
    let response = await sendRequest(`${server}/api/clubs/${clubID}`, "POST")
    if ("error" in response){
        updateModalContent("Join Club", `${response["error"]}`)
    } else {
        updateModalContent("Join Club", `${response["message"]}`)
    }
}

async function leaveClub(clubID){
    let response = await sendRequest(`${server}/api/myClubs/${clubID}`, "DELETE")
    if ("error" in response){
        updateModalContent("Leave Club", `${response["error"]}`)
    } else {
        updateModalContent("Leave Club", `${response["message"]}`)
    }
    getAllMyClubs()
}

function main(){
    document.forms["signUpForm"].addEventListener("submit", signUp)
    document.forms["loginForm"].addEventListener("submit", login)
    document.querySelector("#club-tab").addEventListener("click", getAllClubs)
    document.querySelector("#myClubs-tab").addEventListener("click", getAllMyClubs)
    let logoutButton = document.querySelector("#logoutButton")
    logoutButton.addEventListener("click", logout)
    $('.toast').toast({"delay" : 3000})
    determineSessionContext()
    getAllClubs()
}

document.addEventListener('DOMContentLoaded', main)