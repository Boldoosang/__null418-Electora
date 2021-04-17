//const server = "https://electora.herokuapp.com"
const server = "http://localhost:8080"
console.log(server)
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
        updateToastContent("Login", `Login failed! ${result["error"]}.`)
    } else {
        updateToastContent("Login", `Login successful!`)

        window.localStorage.setItem('access_token', result['access_token']);
        window.location = `${server}`
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

    form.reset()

    let result = await sendRequest(`${server}/register`, "POST", data)

    if("error" in result) {
        updateToastContent("Electora Registration", `Sign up failed! ${result["error"]}.`)
    } else {
        updateToastContent("Electora Registration", `${result["message"]}.`)
    }
    $('#signUpModal').modal('hide')
}

function updateToastContent(newToastTitle, newToastContent){
    let toastTitle = document.querySelector("#genericToastTitle")
    let toastBody = document.querySelector("#genericToastMessage")

    toastTitle.innerHTML = newToastTitle
    toastBody.innerHTML = newToastContent
    $('.toast').toast("show")
}

function logout(){
    accessToken = window.localStorage.getItem("access_token");
    if(accessToken){
        window.localStorage.removeItem('access_token');
        updateToastContent("Logout", "Succesfully logged out!")
    } else {
        updateToastContent("Logout", "You were not logged in!")
    }
    determineSessionContext()
    window.location = `${server}`
}

async function determineSessionContext(){
    identification = await sendRequest(`${server}/identify`, "GET")
    let logoutButton = document.querySelector("#logoutButton")

    if(!("error" in identification)){
        username = await sendRequest(`${server}/identify`, "GET")
        logoutButton.innerText = "Logout"
        navbarLinks.innerHTML = `
                                <li class="nav-item">
                                    <a class="nav-link" href="#">Logged in as ${identification.username}!</a>
                                </li>`
    } else {
        logoutButton.innerText = ""
        navbarLinks.innerHTML = `<li class="nav-item">
                                    <a class="nav-link text-info" id="navLink1" href="#" data-toggle="modal" data-target="#loginModal">Login</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link text-info" id="navLink2" href="#" data-toggle="modal" data-target="#signUpModal">Register</a>
                                </li>`
    }
    
}

async function displayClubs(clubs){
    clubArea = document.querySelector("#clubDisplayArea")
    let listOfClubs = ""
    if(clubs.length > 0){  
        for(club of clubs){
            listOfClubs += `<div class="col-sm-6 mt-3">
                              <div class="card bg-secondary" style="width: 100%;">
                                <img class="card-img-top" src="${club["clubImage"]}">
                                <div class="card-body">
                                  <h5 class="card-title text-info">${club["clubName"]}</h5>
                                  <p class="card-text text-white">${club["clubDescription"]}</p>
                                  <a href="#" onclick="joinClub(${club["clubID"]})" class="btn btn-info">Join Club</a>
                                </div>
                              </div>
                            </div> `
        }
        
        clubDisplayArea.innerHTML = listOfClubs
        
    } else {
        updateToastContent("Clubs", "No clubs have been added yet!")
    }
}


async function getAllClubs(){
    let clubs = await sendRequest(`${server}/api/clubs`, "GET")

    let clubDisplayArea = document.querySelector("#clubDisplayArea")

    if(clubs != null){
        if ("error" in clubs){
            updateToastContent("View My Clubs", `No clubs yet!`)
            clubDisplayArea.innerHTML = 
            `<div class="col-sm-12 mt-3 text-center"">
                <h5>No clubs have been created!</h5>
                <p>Sorry, but there hasn't been any clubs added to this application.</p>
            </div> `
        } else {
            displayClubs(clubs)
        }
    }
}


async function displayMyClubs(myClubs){
    myClubsArea = document.querySelector("#myClubsDisplayArea")
    let listOfClubs = ""
    if(myClubs.length > 0){
        for(myClub of myClubs){
            listOfClubs += `<div class="col-sm-6 mt-3">
                              <div class="card">
                                <img class="card-img-top" src="${myClub["clubImage"]}">
                                <div class="card-body bg-secondary">
                                  <h5 class="card-title text-info">${myClub["clubName"]}</h5>
                                  <p class="card-text text-white">${myClub["clubDescription"]}</p>
                                  <a href="#" onclick="leaveClub(${myClub["clubID"]})" class="btn btn-info">Leave club</a>
                                </div>
                              </div>
                            </div> `
        }
        
        myClubsArea.innerHTML = listOfClubs
    } else {
        myClubsArea.innerHTML = 
        `<div class="col-sm-12 mt-3 text-center">
            <h5>No Joined Clubs</h5>
            <p>Sorry, but you are not a member of any club. You can join a club via the 'Clubs' tab.</p>
        </div> `
    }

}

async function getAllMyClubs(){
    let myClubs = await sendRequest(`${server}/api/myClubs`, "GET")
    let myClubsArea = document.querySelector("#myClubsDisplayArea")
    try {
        if ("error" in myClubs){
            updateToastContent("View My Clubs", `Not logged in!`)
            myClubsArea.innerHTML = 
            `<div class="col-sm-12 mt-3 text-center"">
                <h5>Not logged in!</h5>
                <p>Sorry, but you need to be logged in to view your clubs.</p>
            </div> `
        } else {
            displayMyClubs(myClubs)
        }
    } catch(e){
        //Error generated when there are no clubs
        updateToastContent("View My Clubs", `No clubs yet!`)
        myClubsArea.innerHTML = 
        `<div class="col-sm-12 mt-3 text-center"">
            <h5>No clubs have been created!</h5>
            <p>Sorry, but there hasn't been any clubs added to this application.</p>
        </div> `
    }
}


async function displayMyActiveElections(myElections){
    activeElectionsArea = document.querySelector("#activeElectionsDisplayArea")
    let listOfElections = ""
    let openElections = 0

    /*
    if(myElections != null){
        myElections.filter(function (el) {
            return el != null;
        });
        if(myElections[0] == null)
            myElections = null
    }
    */

    if((myElections != null)) {
        if(myElections.length > 0){
            for(clubElection of myElections){
                listOfCandidates = ""
                let electionStatus = `<h3>Closed Election</h3>`
                if(clubElection.isOpen){
                    electionStatus = `<h3>Open Election</h3>`
                    openElections++
                } else
                    continue
                for(candidate of clubElection.candidates)
                    listOfCandidates += `<div class="card mt-3 bg-dark col-lg-5 mx-3">
                                            <div class="row d-flex align-items-center">
                                                <div class="d-flex align-items-center col-xs-2 h-75 w-25">
                                                    <input class="h-100 w-75 ml-3 position-relative" type="radio" name="${clubElection.clubID}" id="candidate-${candidate["candidateID"]}" value="${candidate["candidateID"]}">
                                                </div>
                                                <div class="col-xs-10 pl-0">
                                                    <div class="card-body col-xs-12">
                                                        <h5 class="card-title">${candidate["firstName"]} ${candidate["lastName"]}</h5>
                                                        <p class="card-text">${candidate["numVotes"]} votes</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>`

                listOfElections += `<div class="col-sm-12 mt-3">
                                        <div class="card">
                                            <div class="jumbotron">
                                                <h1 class="display-4">${clubElection["position"]}</h1>
                                                <p class="lead">${clubElection["clubName"]}</p>
                                                <hr class="my-4">
                                                <h5>${electionStatus}</h5>
                                            </div>
                                            <div class="card-body">
                                                <a style="width: 100%;" class="btn btn-success" data-toggle="collapse" href="#election-${clubElection["electionID"]}" role="button">Vote</a>
                                                <div class="collapse" id="election-${clubElection["electionID"]}">
                                                    <form onsubmit = "castVote(event, ${clubElection["electionID"]})">
                                                        <div class="row justify-content-between">
                                                            ${listOfCandidates}
                                                        </div>
                                                        <div class="text-center mt-4">
                                                            <hr class="my-4">
                                                            <input type="submit" style="width: 50%;" value="Cast Vote" class="btn btn-primary" role="button">
                                                        </div>
                                                    </form>
                                                </div>
                                            </div>
                                        </div>
                                    </div> `
                
            }
            activeElectionsArea.innerHTML = listOfElections
            
        } 
    } 
    if(openElections <= 0){
        activeElectionsArea.innerHTML = 
        `<div class="col-sm-12 mt-3 text-center"">
            <h5>No Active Elections</h5>
            <p>Sorry, but there are currently no available active elections. You can start an election in the 'Host Election' tab.</p>
        </div> `
    }

}

//Does not show appropriate message for closed elections
async function getAllMyActiveElections(){
    
    identification = await sendRequest(`${server}/identify`, "GET")

    if("error" in identification){
        updateToastContent("View Active Elections", `Not logged in!`)
        activeElectionsArea = document.querySelector("#activeElectionsDisplayArea")
        activeElectionsArea.innerHTML = 
        `<div class="col-sm-12 mt-3 text-center"">
            <h5>Not logged in!</h5>
            <p>Sorry, but you need to be logged in to view the active elections.</p>
        </div> `
    } else {
        let elections = await sendRequest(`${server}/api/elections`, "GET")
        displayMyActiveElections(elections)
    }
}


async function getMyPastElections(){
    identification = await sendRequest(`${server}/identify`, "GET")
    let pastElectionsArea = document.querySelector("#pastElectionsDisplayArea")
    if("error" in identification){
        updateToastContent("Past Elections", `Not logged in!`)
        pastElectionsArea.innerHTML = 
        `<div class="col-sm-12 mt-3 text-center">
            <h5>Not logged in!</h5>
            <p>Sorry, but you need to be logged in to view the past elections of your clubs.</p>
        </div> `
    } else {
        let myClubs = await sendRequest(`${server}/api/myClubs`, "GET")
        pastElectionsArea.innerHTML = ` 
        
            <div class="container row d-flex justify-content-center mt-3">
                <div class="col-lg-4">
                    <div class="bg-light nav flex-column nav-pills p-3 mt-3" id="pastElectionClubList" role="tablist"></div>
                </div>
                <div class="col-lg-8" id="pastElectionDisplayArea">
                    <div class="col-sm-12 mt-3 text-center">
                        <h5>Select a club</h5>
                        <p>To view the election details of previous elections, please select a club from the menu.</p>
                    </div>
                </div>

            </div>
        
                                        `
        displayMyPastElectionsMenu(myClubs)
    }
  }

async function displayMyPastElectionsMenu(myClubs){
    let pastElectionClubList = document.querySelector("#pastElectionClubList")
    let listOfClubs = ""

    if(myClubs != null && myClubs.length > 0){
        for(myClub of myClubs){
            listOfClubs += ` <a role="tab" data-toggle="pill"  value="${myClub["clubID"]}" onclick="displayMyPastElectionsDetails(${myClub["clubID"]})"  class="peClubList nav-link" href="#">${myClub["clubName"]}</a>`
        }   
        pastElectionClubList.innerHTML = listOfClubs
    } else {
        let pastElectionsArea = document.querySelector("#pastElectionsDisplayArea")
        pastElectionsArea.innerHTML = 
        `<div class="col-sm-12 mt-3 text-center"">
            <h5>No Joined Clubs</h5>
            <p>Sorry, but you are not a member of any club. You can join a club via the 'Clubs' tab to view past elections for this club.</p>
        </div> `
    }

}

var graphCandidates = []
async function displayMyPastElectionsDetails(clubID){
    let pastElectionDisplayArea = document.querySelector("#pastElectionDisplayArea")
    let myPastElections = await sendRequest(`${server}/api/elections`, "GET")
    let closedCount = 0;
    let listOfElections = ""

    if((myPastElections != null)) {
        if(myPastElections.length > 0){
            myPastElections.reverse()
            for(clubElection of myPastElections){
                if(clubElection.clubID == clubID){
                    let electionStatus = `<h3>Open Election</h3>`
                    if(!clubElection.isOpen) {
                        electionStatus = `<h3>Closed Election</h3>`
                        closedCount++;
                    } else
                        continue
                    
                    listOfCandidates = ""
                    graphCandidates = []
                    for(candidate of clubElection.candidates){
                        var cardColor;
                        if((candidate.firstName + " " + candidate.lastName) == clubElection.electionWinner)
                            cardColor = "bg-success"
                        else if("Tie" == clubElection.electionWinner)
                            cardColor = "bg-secondary"
                        else
                            cardColor = "bg-danger"
                        
                        listOfCandidates += `<div class="card mt-3 col-lg-5 mx-3 ${cardColor}">
                                                <div class="card-body col-sm-12">
                                                    <h5 class="card-title">${candidate["firstName"]} ${candidate["lastName"]}</h5>
                                                    <p class="card-text">${candidate["finalNumVotes"]} total votes</p>
                                                </div>
                                            </div>`
                        graphCandidates.push(candidate)
                    }
                    
                    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                    let electionDate = new Date(clubElection["electionEndDate"])

                    electionDate = electionDate.toLocaleDateString("en-TT", options)
                    listOfElections += `<div class="col-sm-12 mt-3">
                                        <div class="card">
                                            <div class="jumbotron">
                                                <h1 style="font-size: 4em;">${clubElection["electionWinner"]}</h1>
                                                <h2 class="display-4">${clubElection["position"]}</h2>
                                                <p class="lead">${clubElection["clubName"]}</p>
                                                <hr class="my-4">
                                                <h5>${electionStatus}${electionDate}</h5>
                                            </div>
                                            <div class="card-body">
                                                <a class="w-100 btn btn-info" data-toggle="collapse" href="#election-${clubElection["electionID"]}" role="button">Election Details</a>
                                                <div class="collapse" id="election-${clubElection["electionID"]}">
                                                    <form onsubmit = "generateElectionGraph(event, ${clubElection["electionID"]})">
                                                        <div class="row justify-content-between">
                                                            ${listOfCandidates}
                                                        </div>
                                                        <div class="text-center mt-4">
                                                            <hr class="my-4">
                                                            <a style="width: 25%;" class="btn btn-info" href="#" data-toggle="modal" data-target="#electionResultModal" onclick="electionPieChart(graphCandidates)" id="electionPieChart">More Info</a>
                                                            <a style="width: 25%;" class="btn btn-danger" data-toggle="collapse" href="#election-${clubElection["electionID"]}" role="button">Close</a>
                                                        </div>
                                                    </form>
                                                </div>
                                            </div>
                                        </div>
                                    </div> `
                    //
                }
            }
            pastElectionDisplayArea.innerHTML = listOfElections
            
        } 
    }
    if(closedCount <= 0){
        pastElectionDisplayArea.innerHTML = 
        `<div class="col-sm-12 mt-3 text-center"">
            <h5>No Past Elections for this Club</h5>
            <p>Sorry, but there are no past elections for this club. You can start an election by clicking on the 'Host Election' tab.</p>
        </div> `
    }

}

function electionPieChart(graphCandidates){
    let content = document.querySelector("#electionResultPieChart")
    content.innerHTML = ""

    var data = []
    for (candidate of graphCandidates){
        rec = {x: candidate["firstName"], value: candidate["finalNumVotes"]}
        data.push(rec)
    }
    var chart = anychart.pie()
    chart.title("Pie Chart of Election Results")
    chart.data(data)
    chart.container('electionResultPieChart')
    chart.draw()
 }

  async function displayMyPastElections(clubID){
    let pastElections= document.querySelector('#clubPastElections')
    pastElections.innerHTML=""
    let elections = await sendRequest(`${server}/api/clubs/${clubID}/getPastElections`, "GET")
    
    for(election of elections){
      pastElections.innerHTML+=
      `
      <div class="jumbotron">
        <h1 class="display-4">Election Winner: ${election["electionWinner"]}</h1>
        <p class="lead">Position: ${election["position"]}</p>
        <p class="lead">End Date: ${election["Election End Date"]}</p>
        <hr class="my-4">
        <p class="lead">
        <a class="btn btn-primary btn-lg" href="#" role="button">Learn more</a>
        </p>
      </div>
      `
    }      
  }

async function joinClub(clubID){
    let response = await sendRequest(`${server}/api/clubs/${clubID}`, "POST")
    if ("error" in response){
        updateToastContent("Join Club", `${response["error"]}`)
    } else {
        updateToastContent("Join Club", `${response["message"]}`)
    }
}

async function castVote(event, electionID){
    event.preventDefault()

    let form = event.target
    let checkedElement

    for(element of form){
        if(element.checked)
            checkedElement = element.value
    }

    let candidateID = checkedElement

    let response = await sendRequest(`${server}/api/elections/${electionID}/candidates/${candidateID}`, "POST")
    if ("error" in response){
        updateToastContent("Vote for Candidate", `${response["error"]}`)
    } else {
        updateToastContent("Vote for Candidate", `${response["message"]}`)
    }
    getAllMyActiveElections()
}

async function leaveClub(clubID){
    let response = await sendRequest(`${server}/api/myClubs/${clubID}`, "DELETE")
    if ("error" in response){
        updateToastContent("Leave Club", `${response["error"]}`)
    } else {
        updateToastContent("Leave Club", `${response["message"]}`)
    }
    getAllMyClubs()
}

async function displayElectionsManager(){
    let optionList=document.querySelector('#electionOptions')
    let content=document.querySelector('#electionContent')
    
    let myClubs = await sendRequest(`${server}/api/myClubs`, "GET")

    if('error' in myClubs){
      optionList.innerHTML=""
      updateToastContent("Host Elections", `Not logged in!`)

      let noLogin=document.querySelector('#hostElectionContentArea')
      noLogin.innerHTML=
      `<div class="col-sm-12 mt-3 text-center">
        <h5>Not logged in!</h5>
        <p>Sorry, but you need to be logged in to view the past elections of your clubs.</p>
      </div>`
    }else if(myClubs.length == 0){
        optionList.innerHTML=""
        let noClubs=document.querySelector('#hostElectionContentArea')
        noClubs.innerHTML=
        `<div class="col-sm-12 mt-3 text-center">
          <h5>No Clubs</h5>
          <p>Sorry, but you need to be a member of a club to manage an election.</p>
        </div>`
    }else{
    content.innerHTML=`
    <div class="container row d-flex justify-content-center mt-3">
                    <div class="col-sm-12 mt-3 text-center">
                        <h5>Select an Option</h5>
                        <p>Select an option to manage elections.</p>
                </div>

            </div>
    `
    optionList.innerHTML=`
      <button type="button" class="btn btn-outline-info btn-lg btn-block" onclick="displayAddElection()">Add Election</button>
      <button type="button" class="btn btn-outline-info btn-lg btn-block" onClick="addCandidateToExisting()">Add Candidate</button>
      <button type="button" class="btn btn-outline-info btn-lg btn-block" onClick="closeElection()">Close Election</button>
      <button type="button" class="btn btn-outline-info btn-lg btn-block" onClick="removeCandidate()">Remove Candidate</button>
      <button type="button" class="btn btn-outline-info btn-lg btn-block" onClick="updateCandidate()">Update Candidate</button>
      <button type="button" class="btn btn-outline-info btn-lg btn-block" onClick="deleteElection()">Delete Election</button>
      `
    }
}

async function displayAddElection(){
    let content=document.querySelector('#electionContent')
    content.innerHTML=
    `
    <form id="createElectionForm">
      <div class="form-group">
        <label for="clubInput" class="text-white">Choose Club</label>
        <select class="form-control" id="clubInput"></select>
      </div>
      
      <div class="form-group">
        <label for="positionInput" class="text-white">Election Position</label>
        <input type="text" class="form-control" id="positionInput">
      </div>

      <div id="candidate">
        <div class="form-group" id="candidate" >
          <label for="nameInput" class="text-white">Candidate Name</label>
          <input type="text" class="form-control" placeholder="First Name">
          <input type="text" class="form-control" placeholder="Last Name">
        </div>
      </div>

      <button type="button" class="btn btn-outline-info" onClick="addCandidate()">Add Candidate</button>
      <button id="electionSubmit" type="submit" class="btn btn-info">Begin Election</button>
    </form>
    `

    let clubOptions=document.querySelector("#clubInput")
    clubOptions.innerHTML= "<option selected>Choose...</option>"

    let myClubs = await sendRequest(`${server}/api/myClubs`, "GET")
    for(club of myClubs){
      clubOptions.innerHTML+=`<option value="${club['clubID']}">${club["clubName"]}</option>`
    }

    document.forms["createElectionForm"].addEventListener("submit", createElection)
}

async function addCandidateToExisting(){
    let content=document.querySelector('#electionContent')

    content.innerHTML=`
    <form id="AddCandidateChooseElection">
      <div class="form-group">
      <label for="electionInput" class="text-white">Choose Election</label>
      <select class="form-control" id="electionInput"></select>
      </div> 
      <button id="electionSubmit" type="submit" class="btn btn-info">Select Election</button>
    </form>
    `

    let electionOptions=document.querySelector("#electionInput")
    
    let electionss = await sendRequest(`${server}/api/myElections`, "GET")
    console.log(electionss)
    let elections = electionss
        for(election of elections){
            if(election){
                if(election['isOpen'] == true){
                    electionOptions.innerHTML+=`<option value="${election['electionID']}">${election["position"]} ${election["clubName"]}</option>`
                }
            }
        }

    document.forms["AddCandidateChooseElection"].addEventListener("submit", async function(event){
        event.preventDefault()
        let form = event.target.elements

        electionID = form['electionInput'].value

        let candidates = await sendRequest(`${server}/api/elections/${electionID}/candidates`, "GET")

        let newForm = document.querySelector("#electionContent")

        newForm.innerHTML+=`
            <form id="AddCandidateChoose">
                <div class="form-group">
                    <label for="candidateInput">Choose Candidate</label>
                    <select class="form-control" id="candidateInput"></select>
                </div>

                <div class="form-group" id="newFname">
                    <label for="fnameInput">New First Name</label>
                    <input type="text" class="form-control" id="fnameInput" placeholder="First Name">
                </div>

                <div class="form-group" id="newLname">
                    <label for="lnameInput">New Last Name</label>
                    <input type="text" class="form-control" id="lnameInput" placeholder="Last Name">
                </div>
                <button id="candidateSubmit" type="submit" class="btn btn-primary">Add Candidate</button>
            </form>
            `
        
        let candidateOptions=document.querySelector("#candidateInput")

        for(candidate of candidates){
                candidateOptions.innerHTML+=`<option value="${candidate['candidateID']}">${candidate['firstName']} ${candidate['lastName']}</option>`
        }

        document.forms["AddCandidateChoose"].addEventListener("submit", async function(event){
            event.preventDefault()
            let form = event.target.elements

            let data = {
                firstName: form['fnameInput'].value,
                lastName: form['lnameInput'].value
            }
            let response = await sendRequest(`${server}/api/elections/${electionID}/candidates`, "POST", data)
        })
    })
}

async function deleteElection(){
    let content=document.querySelector('#electionContent')

    content.innerHTML=`
    <form id="deleteElectionForm">
      <div class="form-group">
        <label for="electionInput" class="text-white">Choose Election</label>
        <select class="form-control" id="electionInput"></select>
      </div> 
      <button id="electionSubmit" type="submit" class="btn btn-info">Delete Election</button>
    </form>
    `
    let electionOptions=document.querySelector("#electionInput")

    let elections = await sendRequest(`${server}/api/myElections`, "GET")
        for(election of elections){
            if(election){
                if(election[0]['isOpen'] == true){
                    electionOptions.innerHTML+=`<option value="${election[0]['electionID']}">${election[0]["position"]} ${election[0]["clubName"]}</option>`
                }
            }
        }
    document.forms["deleteElectionForm"].addEventListener("submit", async function(event){
        event.preventDefault()
        let form = event.target.elements

        let electionID = form['electionInput'].value
        
        let response = await sendRequest(`${server}/api/elections/${electionID}`, "DELETE")
        })
}

async function removeCandidate(){
    let content=document.querySelector('#electionContent')

    content.innerHTML=`
    <form id="removeCandidateChooseElection">
      <div class="form-group">
      <label for="electionInput" class="text-white">Choose Election</label>
      <select class="form-control" id="electionInput"></select>
      </div> 
      <button id="electionSubmit" type="submit" class="btn btn-info">Select Election</button>
    </form>
    `

    let electionOptions=document.querySelector("#electionInput")

    let elections = await sendRequest(`${server}/api/myElections`, "GET")
        for(election of elections){
            if(election){
                if(election[0]['isOpen'] == true){
                    electionOptions.innerHTML+=`<option value="${election[0]['electionID']}">${election[0]["position"]} ${election[0]["clubName"]}</option>`
                }
            }
        }

    document.forms["removeCandidateChooseElection"].addEventListener("submit", async function(event){
        event.preventDefault()
        let form = event.target.elements

        electionID = form['electionInput'].value

        let candidates = await sendRequest(`${server}/api/elections/${electionID}/candidates`, "GET")

        let newForm = document.querySelector("#electionContent")

        newForm.innerHTML+=`
            <form id="removeCandidateChoose">
                <div class="form-group">
                    <label for="candidateInput">Choose Candidate</label>
                    <select class="form-control" id="candidateInput"></select>
                </div> 
                <button id="candidateSubmit" type="submit" class="btn btn-primary">Remove Candidate</button>
            </form>
            `
        
        let candidateOptions=document.querySelector("#candidateInput")

        for(candidate of candidates){
                candidateOptions.innerHTML+=`<option value="${candidate['candidateID']}">${candidate['firstName']} ${candidate['lastName']}</option>`
        }

        document.forms["removeCandidateChoose"].addEventListener("submit", async function(event){
            event.preventDefault()
            let form = event.target.elements

            let candidateID = form['candidateInput'].value

            let response = await sendRequest(`${server}/api/elections/${electionID}/candidates/${candidateID}`, "DELETE")
        })
    })    
}

async function updateCandidate(){
    let content=document.querySelector('#electionContent')

    content.innerHTML=`
    <form id="updateCandidateChooseElection">
      <div class="form-group">
      <label for="electionInput" class="text-white">Choose Election</label>
      <select class="form-control" id="electionInput"></select>
      </div> 
      <button id="electionSubmit" type="submit" class="btn btn-info">Select Election</button>
    </form>
    `

    let electionOptions=document.querySelector("#electionInput")

    let elections = await sendRequest(`${server}/api/myElections`, "GET")
        for(election of elections){
            if(election){
                if(election[0]['isOpen'] == true){
                    electionOptions.innerHTML+=`<option value="${election[0]['electionID']}">${election[0]["position"]} ${election[0]["clubName"]}</option>`
                }
            }
        }

    document.forms["updateCandidateChooseElection"].addEventListener("submit", async function(event){
        event.preventDefault()
        let form = event.target.elements

        electionID = form['electionInput'].value


        let candidates = await sendRequest(`${server}/api/elections/${electionID}/candidates`, "GET")

        let newForm = document.querySelector("#electionContent")

        newForm.innerHTML+=`
            <form id="updateCandidateChoose">
                <div class="form-group">
                    <label for="candidateInput">Choose Candidate</label>
                    <select class="form-control" id="candidateInput"></select>
                </div>

                <div class="form-group" id="newFname">
                    <label for="fnameInput">New First Name</label>
                    <input type="text" class="form-control" id="fnameInput" placeholder="First Name">
                </div>

                <div class="form-group" id="newLname">
                    <label for="lnameInput">New Last Name</label>
                    <input type="text" class="form-control" id="lnameInput" placeholder="Last Name">
                </div>
                <button id="candidateSubmit" type="submit" class="btn btn-primary">Update Candidate</button>
            </form>
            `
        
        let candidateOptions=document.querySelector("#candidateInput")

        for(candidate of candidates){
                candidateOptions.innerHTML+=`<option value="${candidate['candidateID']}">${candidate['firstName']} ${candidate['lastName']}</option>`
        }

        document.forms["updateCandidateChoose"].addEventListener("submit", async function(event){
            event.preventDefault()
            let form = event.target.elements

            let candidateID = form['candidateInput'].value

            let data = {
                firstName: form['fnameInput'].value,
                lastName: form['lnameInput'].value
            }

            let response = await sendRequest(`${server}/api/elections/${electionID}/candidates/${candidateID}`, "PUT", data)
        })
    })
}

async function closeElection(){
    let content=document.querySelector('#electionContent')
    content.innerHTML=`
    <form id="closeElectionForm">
      <div class="form-group">
        <label for="electionInput" class="text-white">Choose Election</label>
        <select class="form-control" id="electionInput"></select>
      </div> 
      <button id="electionSubmit" type="submit" class="btn btn-info">Close Election</button>
    </form>
    `
    let electionOptions=document.querySelector("#electionInput")

    let elections = await sendRequest(`${server}/api/myElections`, "GET")
        for(election of elections){
            if(election){
                if(election[0]['isOpen'] == true){
                    electionOptions.innerHTML+=`<option value="${election[0]['electionID']}">${election[0]["position"]} ${election[0]["clubName"]}</option>`
                }
            }
        }
    document.forms["closeElectionForm"].addEventListener("submit", async function(event){
        event.preventDefault()
        let form = event.target.elements

        clubID = form['electionInput'].value

        data = {
            "isOpen" : false
        }

        let response = await sendRequest(`${server}/api/elections/${clubID}`, "PUT", data)
        })
}

async function addCandidate(){
    let content=document.querySelector('#candidate')

    content.innerHTML+=
    `
        <div class="form-group" id="candidate">
          <label for="nameInput">Candidate Name</label>
          <input type="text" class="form-control" placeholder="First Name">
          <input type="text" class="form-control" placeholder="Last Name">
        </div>
    `
}

async function createElection(event){
    event.preventDefault()
    const names = document.querySelector('#candidate')
    let fields = names.querySelectorAll('input')
    let cnames = []
    let name = []
    let fname
    let lname
    i=0

    for(field of fields){
      if(i==0){
        fname = field['value']  
        i=1
        continue
      }
      if(i==1){
        lname = field['value']
        name={
          "firstName": fname,
          "lastName": lname
        }
        
        cnames.push(name)
        name = {}
        i=0
      }
    }

    let form = event.target.elements
    
    let data={
      clubID: form['clubInput'].value,
      position: form['positionInput'].value,
      candidates: cnames
    }

    let response = await sendRequest(`${server}/api/elections`, "POST", data)
  }

function main(){
    document.forms["signUpForm"].addEventListener("submit", signUp)
    document.forms["loginForm"].addEventListener("submit", login)
    document.querySelector("#club-tab").addEventListener("click", getAllClubs)
    document.querySelector("#myClubs-tab").addEventListener("click", getAllMyClubs)
    document.querySelector("#activeElections-tab").addEventListener("click", getAllMyActiveElections)
    document.querySelector("#hostElection-tab").addEventListener("click", displayElectionsManager)
    document.querySelector("#pastElections-tab").addEventListener("click", getMyPastElections)
    let logoutButton = document.querySelector("#logoutButton")
    logoutButton.addEventListener("click", logout)
    $('.toast').toast({"delay" : 3000})
    determineSessionContext()
    getAllClubs()
}

document.addEventListener('DOMContentLoaded', main)