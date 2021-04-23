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

    let result = await sendRequest(`/auth`, "POST", data)

    if("error" in result) {
        updateToastContent("Login", `Login failed! ${result["error"]}.`)
    } else {
        updateToastContent("Login", `Login successful!`)

        window.localStorage.setItem('access_token', result['access_token']);
        window.location = `/`
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

    let result = await sendRequest(`/register`, "POST", data)

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
    /*
    let toastAlert = document.querySelector("#toastAlert")
    toastAlert.innerHTML = `<div class="toast" role="alert" style="position: sticky; bottom: 0; left: 0; min-width: 300px; min-height: 100px; margin-left: 10px; margin-bottom: 10px">
                                <div class="toast-header">
                                    <strong id="genericToastTitle" style="min-width: 400px" class="mr-auto">${toastTitle}</strong>
                                    <button type="button" class="ml-2 mb-1 close" data-dismiss="toast"></button>
                                </div>
                                <div id="genericToastMessage" class="toast-body">
                                    ${toastBody}
                                </div>
                            </div>`*/
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
    window.location = `/`
}

async function determineSessionContext(){
    identification = await sendRequest(`/identify`, "GET")
    let logoutButton = document.querySelector("#logoutButton")
    if(!("error" in identification)){
        username = await sendRequest(`/identify`, "GET")
        logoutButton.innerText = "Logout"
        navbarLinks.innerHTML = `
                                <li class="nav-item">
                                    <a class="nav-link text-info" href="#">Logged in as <b class="text-white">${identification.username}</b>!</a>
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
            listOfClubs += `<div class="col-md-6 mt-3">
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
    let clubs = await sendRequest(`/api/clubs`, "GET")

    let clubDisplayArea = document.querySelector("#clubDisplayArea")

    if(clubs != null){
        if ("error" in clubs){
            updateToastContent("View My Clubs", `No clubs yet!`)
            clubDisplayArea.innerHTML = 
            `<div class="col-sm-12 mt-3 text-center text-white">
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
                              <div class="card bg-secondary">
                                <img class="card-img-top" src="${myClub["clubImage"]}">
                                <div class="card-body">
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
        `<div class="col-sm-12 mt-3 text-center text-white">
            <h5>No Joined Clubs</h5>
            <p>Sorry, but you are not a member of any club. You can join a club via the 'Clubs' tab.</p>
        </div> `
    }
}


async function getAllMyClubs(){
    let myClubsArea = document.querySelector("#myClubsDisplayArea")
    identification = await sendRequest(`/identify`, "GET")

    if ("error" in identification){
        updateToastContent("View My Clubs", `Not logged in!`)
        myClubsArea.innerHTML = 
        `<div class="col-sm-12 mt-3 text-center text-white">
            <h5>Not logged in!</h5>
            <p>Sorry, but you need to be logged in to view your clubs.</p>
        </div> `
    } else {
        let myClubs = await sendRequest(`/api/myClubs`, "GET")
        displayMyClubs(myClubs)
    }
}


async function displayMyActiveElections(myElections){
    activeElectionsArea = document.querySelector("#activeElectionsDisplayArea")
    let listOfElections = ""
    let openElections = 0

    if((myElections != null)) {
        if(myElections.length > 0){
            for(clubElection of myElections){
                listOfCandidates = ""
                let electionStatus = `<h3 class="text-white">Closed Election</h3>`
                if(clubElection.isOpen){
                    electionStatus = `<h3 class="text-white">Open Election</h3>`
                    openElections++
                } else
                    continue
                for(candidate of clubElection.candidates)
                    listOfCandidates += `<div class="card mt-3 bg-primary col-lg-5 mx-3">
                                            <div class="row d-flex align-items-center">
                                                <div class="d-flex align-items-center col-xs-2 h-75 w-25">
                                                    <input class="h-100 w-75 ml-3 position-relative" type="radio" name="${clubElection.clubID}" id="candidate-${candidate["candidateID"]}" value="${candidate["candidateID"]}">
                                                </div>
                                                <div class="col-xs-10 pl-0">
                                                    <div class="card-body col-xs-12">
                                                        <h5 class="card-title text-info">${candidate["firstName"]} ${candidate["lastName"]}</h5>
                                                        <p class="card-text text-white">${candidate["numVotes"]} votes</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>`

                listOfElections += `<div class="col-sm-12 mt-3">
                                        <div class="card bg-secondary">
                                            <div class="jumbotron bg-secondary">
                                                <h1 class="display-4 text-info">${clubElection["position"]}</h1>
                                                <p class="lead text-white">${clubElection["clubName"]}</p>
                                                <hr class="my-4">
                                                <h5 class="text-white">${electionStatus}</h5>
                                            </div>
                                            <div class="card-body">
                                                <a style="width: 100%;" class="btn btn-info" data-toggle="collapse" href="#election-${clubElection["electionID"]}" role="button">Vote</a>
                                                <div class="collapse" id="election-${clubElection["electionID"]}">
                                                    <form onsubmit = "castVote(event, ${clubElection["electionID"]})">
                                                        <div class="row justify-content-between">
                                                            ${listOfCandidates}
                                                        </div>
                                                        <div class="text-center mt-4">
                                                            <hr class="my-4">
                                                            <input type="submit" style="width: 50%;" value="Cast Vote" class="btn btn-info" role="button">
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
        `<div class="col-sm-12 mt-3 text-center text-white">
            <h5>No Active Elections</h5>
            <p>Sorry, but there are currently no available active elections. You can start an election in the 'Host Election' tab.</p>
        </div> `
    }

}

//Does not show appropriate message for closed elections
async function getAllMyActiveElections(){
    
    identification = await sendRequest(`/identify`, "GET")

    if("error" in identification){
        updateToastContent("View Active Elections", `Not logged in!`)
        activeElectionsArea = document.querySelector("#activeElectionsDisplayArea")
        activeElectionsArea.innerHTML = 
        `<div class="col-sm-12 mt-3 text-center text-white">
            <h5>Not logged in!</h5>
            <p>Sorry, but you need to be logged in to view the active elections.</p>
        </div> `
    } else {
        let elections = await sendRequest(`/api/elections`, "GET")
        displayMyActiveElections(elections)
    }
}


async function getMyPastElections(){
    identification = await sendRequest(`/identify`, "GET")
    let pastElectionsArea = document.querySelector("#pastElectionsDisplayArea")
    if("error" in identification){
        updateToastContent("Past Elections", `Not logged in!`)
        pastElectionsArea.innerHTML = 
        `<div class="col-sm-12 mt-3 text-center text-white">
            <h5>Not logged in!</h5>
            <p>Sorry, but you need to be logged in to view the past elections of your clubs.</p>
        </div> `
    } else {
        let myClubs = await sendRequest(`/api/myClubs`, "GET")
        pastElectionsArea.innerHTML = ` 
            <div class="container row d-flex justify-content-center mt-3">
                <div class="col-lg-4">
                    <div class="bg-secondary nav flex-column nav-pills p-3 mt-3" id="pastElectionClubList" role="tablist"></div>
                </div>
                <div class="col-lg-8" id="pastElectionDisplayArea">
                    <div class="col-sm-12 mt-3 text-center text-white">
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
        for(myClub of myClubs)
            listOfClubs += ` <a role="tab" data-toggle="pill"  value="${myClub["clubID"]}" onclick="displayMyPastElectionsDetails(${myClub["clubID"]})"  class="peClubList nav-link text-info" href="#">${myClub["clubName"]}</a>`
        
        pastElectionClubList.innerHTML = listOfClubs
    } else {
        let pastElectionsArea = document.querySelector("#pastElectionsDisplayArea")
        pastElectionsArea.innerHTML = 
        `<div class="col-sm-12 mt-3 text-center text-white">
            <h5>No Joined Clubs</h5>
            <p>Sorry, but you are not a member of any club. You can join a club via the 'Clubs' tab to view past elections for this club.</p>
        </div> `
    }

}

var graphCandidates = []
async function displayMyPastElectionsDetails(clubID){
    let pastElectionDisplayArea = document.querySelector("#pastElectionDisplayArea")
    let myPastElections = await sendRequest(`/api/elections`, "GET")
    let closedCount = 0;
    let listOfElections = ""

    if((myPastElections != null)) {
        if(myPastElections.length > 0){
            myPastElections.reverse()
            for(clubElection of myPastElections){
                if(clubElection.clubID == clubID){
                    let electionStatus = `Open Election`
                    if(!clubElection.isOpen) {
                        electionStatus = `Closed Election`
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
                                                    <h5 class="card-title text-white">${candidate["firstName"]} ${candidate["lastName"]}</h5>
                                                    <p class="card-text text-white">${candidate["finalNumVotes"]} total votes</p>
                                                </div>
                                            </div>`
                        graphCandidates.push(candidate)
                    }
                    
                    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                    let electionDate = new Date(clubElection["electionEndDate"])

                    
                    electionDate = electionDate.toLocaleDateString("en-TT", options)
                    listOfElections += `<div class="col-sm-12 mt-3">
                                        <div class="card bg-secondary">
                                            <div class="jumbotron bg-secondary">
                                                <h1 class= "text-info" style="font-size: 4em;">${clubElection["electionWinner"]}</h1>
                                                <h2 class="display-4 text-white">${clubElection["position"]}</h2>
                                                <p class="lead text-white">${clubElection["clubName"]}</p>
                                                <hr class="my-4 bg-info">
                                                <h2 class="text-white">${electionStatus}</h2>
                                                <h2 class="text-white" style="font-size: 1.7rem">${electionDate}</h2>
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
        `<div class="col-sm-12 mt-3 text-center text-white">
            <h5>No Past Elections for this Club</h5>
            <p>Sorry, but there are no past elections for this club. You can start an election by clicking on the 'Host Election' tab.</p>
        </div> `
    }

}

function electionPieChart(graphCandidates){
    let content = document.querySelector("#electionResultPieChart")
    let children = content.getElementsByTagName('path')

    
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
    children.item(2).style.fill= '#222629'
 }

  async function displayMyPastElections(clubID){
    let pastElections= document.querySelector('#clubPastElections')
    pastElections.innerHTML=""
    let elections = await sendRequest(`/api/clubs/${clubID}/getPastElections`, "GET")
    
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
    let response = await sendRequest(`/api/clubs/${clubID}`, "POST")
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

    let response = await sendRequest(`/api/elections/${electionID}/candidates/${candidateID}`, "POST")
    if ("error" in response){
        updateToastContent("Vote for Candidate", `${response["error"]}`)
    } else {
        updateToastContent("Vote for Candidate", `${response["message"]}`)
    }
    getAllMyActiveElections()
}

async function leaveClub(clubID){
    let response = await sendRequest(`/api/myClubs/${clubID}`, "DELETE")
    if ("error" in response){
        updateToastContent("Leave Club", `${response["error"]}`)
    } else {
        updateToastContent("Leave Club", `${response["message"]}`)
    }
    getAllMyClubs()
}

async function displayElectionsManager(){
    let hostElectionsArea = document.querySelector('#manageElectionDisplayArea')

    identification = await sendRequest(`/identify`, "GET")
    
    if("error" in identification){
      updateToastContent("Host Elections", `Not logged in!`)
      hostElectionsArea.innerHTML =
        `<div class="col-sm-12 mt-3 text-center text-white">
            <h5>Not logged in!</h5>
            <p>Sorry, but you need to be logged in to manage elections of your clubs.</p>
        </div>`

    } else {
        let myClubs = await sendRequest(`/api/myClubs`, "GET")

        if("error" in myClubs){

            hostElectionsArea.innerHTML=
            `<div class="col-sm-12 mt-3 text-center text-white">
                <h5>No Clubs</h5>
                <p>Sorry, but you need to be a member of a club to manage an election.</p>
            </div>`
        } else {
            hostElectionsArea.innerHTML=` 
                                        <div class="col-lg-4">
                                            <div class="nav flex-column p-3 mt-3" id="electionMenuList" role="tablist"></div>
                                        </div>
                                        <div id="electionContent" class="col-lg-8 row d-flex justify-content-center mt-3">
                                            <div class="col-sm-12 mt-3 text-center">
                                                <h5 class="text-white">Select an Option</h5>
                                                <p class="text-white">Select an option to manage elections.</p>
                                            </div>
                                        </div>
                                        `
            optionList = document.querySelector("#electionMenuList")

            optionList.innerHTML=`
            <button type="button" class="btn btn-outline-info btn-lg btn-block" onclick="displayAddElection()">Add Election</button>
            <button type="button" class="btn btn-outline-info btn-lg btn-block" onClick="closeElection()">Close Election</button>
            <button type="button" class="btn btn-outline-info btn-lg btn-block" onClick="openElection()">Open Election</button>
            <button type="button" class="btn btn-outline-info btn-lg btn-block" onClick="deleteElection()">Delete Election</button>
            <button type="button" class="btn btn-outline-info btn-lg btn-block" onClick="addCandidateToExisting()">Add Candidate</button>
            <button type="button" class="btn btn-outline-info btn-lg btn-block" onClick="removeCandidate()">Remove Candidate</button>
            <button type="button" class="btn btn-outline-info btn-lg btn-block" onClick="updateCandidate()">Update Candidate</button>
            
            `
        }
    }
}

async function displayAddElection(){
    let content = document.querySelector('#electionContent')
    content.innerHTML =
    `
    <form id="createElectionForm" class="w-100">
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
          <input type="text" class="form-control mt-3" placeholder="Last Name">
        </div>
      </div>

      <button type="button" class="btn btn-outline-info" onClick="addCandidate()">Add Candidate</button>
      <button id="electionSubmit" type="submit" class="btn btn-info">Begin Election</button>
    </form>
    `

    let clubOptions=document.querySelector("#clubInput")
    clubOptions.innerHTML= "<option selected>Choose...</option>"

    let myClubs = await sendRequest(`/api/myClubs`, "GET")
    if ("error" in myClubs){
        content.innerHTML = `
                            <div class="col-sm-12 mt-3 text-center text-white">
                                <h5>No Clubs</h5>
                                <p>Sorry, but you need to be a member of a club to manage an election.</p>
                            </div>
                            `
    } else {
        for(club of myClubs)
            clubOptions.innerHTML+=`<option class="text-white" value="${club['clubID']}">${club["clubName"]}</option>`

        document.forms["createElectionForm"].addEventListener("submit", createElection)
    }
}

async function addCandidateToExisting(){
    let content=document.querySelector('#electionContent')
    
    let elections = await sendRequest(`/api/myManagingElections`, "GET")

    if("error" in elections){
        content.innerHTML = `
        <div class="col-sm-12 mt-3 text-center text-white">
            <h5>No Active Elections</h5>
            <p>Sorry, but you need to be a manager of an active election to add a candidate.</p>
        </div>
        `
    } else {
        let activeCount = 0
        for(election of elections)
            if(election)
                if(election['isOpen'] == true)
                    activeCount++

        if(activeCount > 0){
            content.innerHTML=`
            <form id="AddCandidateChooseElection" class="w-100">
                <div class="form-group">
                    <label for="electionInput" class="text-white">Choose Election for Adding Candidate</label>
                    <select class="form-control" id="electionInput"></select>
                </div> 
                <button id="electionSubmit" class="btn btn-info">Select Election</button>
            </form>
            `
            let electionOptions = document.querySelector("#electionInput")

            for(election of elections)
                if(election)
                    if(election['isOpen'] == true)
                        electionOptions.innerHTML+=`<option value="${election['electionID']}">${election["position"]} ${election["clubName"]}</option>`
                
 
            document.forms["AddCandidateChooseElection"].addEventListener("submit", async function(event){
                event.preventDefault()
                let form = event.target.elements
        
                electionID = form['electionInput'].value
        
                let newForm = document.querySelector("#electionContent")
        
                newForm.innerHTML+=`
                    <form id="AddCandidateChoose" class="w-100">
                        <div class="form-group text-white" id="newFname">
                            <label for="fnameInput">New First Name</label>
                            <input type="text" class="form-control" id="fnameInput" placeholder="First Name">
                        </div>
        
                        <div class="form-group text-white" id="newLname">
                            <label for="lnameInput">New Last Name</label>
                            <input type="text" class="form-control" id="lnameInput" placeholder="Last Name">
                        </div>
                        <button id="candidateSubmit" type="submit" class="btn btn-primary">Add Candidate</button>
                    </form>
                    `
        
                event.target.reset() 

                document.forms["AddCandidateChoose"].addEventListener("submit", async function(event){
                    event.preventDefault()
                    let form = event.target.elements
        
                    let data = {
                        firstName: form['fnameInput'].value,
                        lastName: form['lnameInput'].value
                    }
                    let response = await sendRequest(`/api/elections/${electionID}/candidates`, "POST", data)
                    event.target.reset()
                    if('error' in response)
                        updateToastContent("Add Candidate", response["error"])
                    else{ 
                        updateToastContent("Add Candidate", "Candidate was successfully added!")
                        addCandidateToExisting()
                    }
                }) 
            })
        } else {
            content.innerHTML = `
            <div class="col-sm-12 mt-3 text-center text-white">
                <h5>No Active Elections</h5>
                <p>Sorry, but you need to be a manager of an active election to add a candidate.</p>
            </div>
            `
        }
    }
}


async function deleteElection(){
    let content=document.querySelector('#electionContent')
    
    let elections = await sendRequest(`/api/myManagingElections`, "GET")

    if("error" in elections){
        content.innerHTML = `
            <div class="col-sm-12 mt-3 text-center text-white">
                <h5>No Closed Elections</h5>
                <p>Sorry, but you need to be a manager of a closed election to delete an election.</p>
            </div>
            `
    } else {
        let closedCount = 0
        for(election of elections)
            if(election)
                if(election['isOpen'] == false)
                    closedCount++

        if(closedCount > 0){
            content.innerHTML = `
            <form id="deleteElectionForm" class="w-100">
            <div class="form-group">
                <label for="electionInput" class="text-white">Choose Election</label>
                <select class="form-control" id="electionInput"></select>
            </div> 
            <button id="electionSubmit" type="submit" class="btn btn-danger">Delete Election</button>
            </form>
            `
            let electionOptions = document.querySelector("#electionInput")

            for(election of elections)
                if(election)
                    if(election['isOpen'] == false)
                        electionOptions.innerHTML+=`<option value="${election['electionID']}">${election["position"]} ${election["clubName"]}</option>`
                
            document.forms["deleteElectionForm"].addEventListener("submit", async function(event){
                event.preventDefault()
                let form = event.target.elements

                let electionID = form['electionInput'].value
                
                let response = await sendRequest(`/api/elections/${electionID}`, "DELETE")
                event.target.reset()

                if("error" in response){
                    updateToastContent("Delete Election", `${response["error"]}`)
                } else {
                    updateToastContent("Delete Election", `Election deleted successfully!`)
                    deleteElection()
                }
            })
        } else {
                content.innerHTML = `
                <div class="col-sm-12 mt-3 text-center text-white">
                    <h5>No Closed Elections</h5>
                    <p>Sorry, but you need to be a manager of a closed election to delete an election.</p>
                </div>
                `
        }
    }
}


async function removeCandidate(){
    let content=document.querySelector('#electionContent')
    
    let elections = await sendRequest(`/api/myManagingElections`, "GET")

    if("error" in elections){
        content.innerHTML = `
        <div class="col-sm-12 mt-3 text-center text-white">
            <h5>No Active Elections</h5>
            <p>Sorry, but you need to be a manager of an active election to remove a candidate.</p>
        </div>
        `
    } else {
        let activeCount = 0
        for(election of elections)
            if(election)
                if(election['isOpen'] == true)
                    activeCount++

        if(activeCount > 0){
            content.innerHTML=`
                <form id="removeCandidateChooseElection" class="w-100">
                <div class="form-group">
                <label for="electionInput" class="text-white">Choose Election for Removing Candidate</label>
                <select class="form-control" id="electionInput"></select>
                </div> 
                <button id="electionSubmit" type="submit" class="btn btn-info">Select Election</button>
                </form>
                `

            let electionOptions = document.querySelector("#electionInput")

            for(election of elections)
                if(election)
                    if(election['isOpen'] == true)
                        electionOptions.innerHTML+=`<option value="${election['electionID']}">${election["position"]} ${election["clubName"]}</option>`
       

            document.forms["removeCandidateChooseElection"].addEventListener("submit", async function(event){
                event.preventDefault()
                let form = event.target.elements
        
                electionID = form['electionInput'].value
        
                let candidates = await sendRequest(`/api/elections/${electionID}/candidates`, "GET")
                
                let newForm = document.querySelector("#electionContent")
                if("error" in candidates){
                    newForm.innerHTML = `
                            <div class="col-sm-12 mt-3 text-center text-white">
                                <h5>No Candidates</h5>
                                <p>Sorry, but there are no candidates for this election.</p>
                            </div>`
                } else {
                    newForm.innerHTML+=`
                        <form id="removeCandidateChoose" class="w-100">
                            <div class="form-group text-white">
                                <label for="candidateInput">Choose Candidate</label>
                                <select class="form-control" id="candidateInput"></select>
                            </div> 
                            <button id="candidateSubmit" type="submit" class="btn btn-primary">Remove Candidate</button>
                        </form>
                        `
                    
                    let candidateOptions=document.querySelector("#candidateInput")
        
                    for(candidate of candidates)
                        candidateOptions.innerHTML+=`<option value="${candidate['candidateID']}">${candidate['firstName']} ${candidate['lastName']}</option>`
                    
        
                    document.forms["removeCandidateChoose"].addEventListener("submit", async function(event){
                        event.preventDefault()
                        let form = event.target.elements
        
                        let candidateID = form['candidateInput'].value
        
                        let response = await sendRequest(`/api/elections/${electionID}/candidates/${candidateID}`, "DELETE")
                        
                        removeCandidate()
        
                        if('error' in response)
                            updateToastContent("Remove Candidate", `${response["error"]}`)
                        else{ 
                            updateToastContent("Remove Candidate", "Candidate was successfully removed!")
                            removeCandidate()
                        }
                    })
                }
            })
        } else {
            content.innerHTML = `
            <div class="col-sm-12 mt-3 text-center text-white">
                <h5>No Active Elections</h5>
                <p>Sorry, but you need to be a manager of an active election to remove a candidate.</p>
            </div>
            `
        }
    } 
}


async function updateCandidate(){
    let content=document.querySelector('#electionContent')
    
    let elections = await sendRequest(`/api/myManagingElections`, "GET")

    if("error" in elections){
        content.innerHTML = `
        <div class="col-sm-12 mt-3 text-center text-white">
            <h5>No Active Elections</h5>
            <p>Sorry, but you need to be a manager of an active election to update a candidate.</p>
        </div>
        `
    } else {
        let activeCount = 0
        for(election of elections)
            if(election)
                if(election['isOpen'] == true)
                    activeCount++

        if(activeCount > 0){
            content.innerHTML=`
                <form id="updateCandidateChooseElection" class="w-100">
                <div class="form-group">
                <label for="electionInput" class="text-white">Choose Election</label>
                <select class="form-control" id="electionInput"></select>
                </div> 
                <button id="electionSubmit" type="submit" class="btn btn-info">Select Election</button>
                </form>
                `

            let electionOptions=document.querySelector("#electionInput")

            for(election of elections)
                if(election)
                    if(election['isOpen'] == true)
                        electionOptions.innerHTML+=`<option value="${election['electionID']}">${election["position"]} ${election["clubName"]}</option>`
            
            document.forms["updateCandidateChooseElection"].addEventListener("submit", async function(event){
                event.preventDefault()
                let form = event.target.elements
    
                electionID = form['electionInput'].value
    
    
                let candidates = await sendRequest(`/api/elections/${electionID}/candidates`, "GET")
                let newForm = document.querySelector("#electionContent")

                if("error" in candidates){
                    newForm.innerHTML = `
                            <div class="col-sm-12 mt-3 text-center text-white">
                                <h5>No Candidates</h5>
                                <p>Sorry, but there are no candidates for this election.</p>
                            </div>`
                } else {
                    newForm.innerHTML+=`
                        <form id="updateCandidateChoose" class="w-100 mt-4">
                            <div class="form-group text-white">
                                <label for="candidateInput">Choose Candidate</label>
                                <select class="form-control" id="candidateInput"></select>
                            </div>
        
                            <div class="form-group text-white" id="newFname">
                                <label for="fnameInput">New First Name</label>
                                <input type="text" class="form-control" id="fnameInput" placeholder="First Name">
                            </div>
        
                            <div class="form-group text-white" id="newLname">
                                <label for="lnameInput">New Last Name</label>
                                <input type="text" class="form-control" id="lnameInput" placeholder="Last Name">
                            </div>
                            <button id="candidateSubmit" type="submit" class="btn btn-primary">Update Candidate</button>
                        </form>
                        `

                    let candidateOptions=document.querySelector("#candidateInput")
    
                    for(candidate of candidates)
                        candidateOptions.innerHTML+=`<option value="${candidate['candidateID']}">${candidate['firstName']} ${candidate['lastName']}</option>`

                    document.forms["updateCandidateChoose"].addEventListener("submit", async function(event){
                        event.preventDefault()
                        let form = event.target.elements
        
                        let candidateID = form['candidateInput'].value
        
                        let data = {
                            firstName: form['fnameInput'].value,
                            lastName: form['lnameInput'].value
                        }
        
                        let response = await sendRequest(`/api/elections/${electionID}/candidates/${candidateID}`, "PUT", data)
                        event.target.reset()

                        if('error' in response)
                            updateToastContent("Update Candidate", `${response["error"]}`)
                        else {
                            updateToastContent("Update Candidate", "Candidate was successfully updated!")
                            updateCandidate()
                        }
                    })
                }
            })

        } else {
            content.innerHTML = `
            <div class="col-sm-12 mt-3 text-center text-white">
                <h5>No Active Elections</h5>
                <p>Sorry, but you need to be a manager of an active election to update a candidate.</p>
            </div>
            `
        }
    }
}



async function closeElection(){
    let content = document.querySelector('#electionContent')
    
    let elections = await sendRequest(`/api/myManagingElections`, "GET")

    if("error" in elections){
        content.innerHTML = `
            <div class="col-sm-12 mt-3 text-center text-white">
                <h5>No Active Elections</h5>
                <p>Sorry, but you need to be a manager of an election to close an election.</p>
            </div>
            `
    } else {
        let activeCount = 0
        for(election of elections)
            if(election)
                if(election['isOpen'] == true)
                    activeCount++

        if(activeCount > 0){
            content.innerHTML = `
            <form id="closeElectionForm" class="w-100">
            <div class="form-group">
                <label for="electionInput" class="text-white">Choose Election</label>
                <select class="form-control" id="electionInput"></select>
            </div> 
            <button id="electionSubmit" type="submit" class="btn btn-danger">Close Election</button>
            </form>
            `
            let electionOptions = document.querySelector("#electionInput")

            for(election of elections)
                if(election)
                    if(election['isOpen'] == true)
                        electionOptions.innerHTML+=`<option value="${election['electionID']}">${election["position"]} ${election["clubName"]}</option>`
                
            document.forms["closeElectionForm"].addEventListener("submit", async function(event){
                event.preventDefault()
                let form = event.target.elements

                electionID = form['electionInput'].value

                data = {
                    "isOpen" : false
                }

                let response = await sendRequest(`/api/elections/${electionID}`, "PUT", data)
                event.target.reset()

                if("error" in response){
                    updateToastContent("Close Election", `${response["error"]}`)
                } else {
                    updateToastContent("Close Election", `Election closed successfully!`)
                    closeElection()
                }
            })
        } else {
                content.innerHTML = `
                <div class="col-sm-12 mt-3 text-center text-white">
                    <h5>No Active Elections</h5>
                    <p>Sorry, but you need to be a manager of an election to close an election.</p>
                </div>
                `
        }
    }
}

async function openElection(){
    let content = document.querySelector('#electionContent')
    
    let elections = await sendRequest(`/api/myManagingElections`, "GET")
    if("error" in elections){
        content.innerHTML = `
            <div class="col-sm-12 mt-3 text-center text-white">
                <h5>No Closed Elections</h5>
                <p>Sorry, but you need to be a manager of an election to open an election.</p>
            </div>
            `
    } else {
        let closedCount = 0
        for(election of elections)
            if(election)
                if(election['isOpen'] == false)
                    closedCount++

        if(closedCount > 0){
            content.innerHTML = `
            <form id="openElectionForm" class="w-100">
            <div class="form-group">
                <label for="electionInput" class="text-white">Choose Election</label>
                <select class="form-control" id="electionInput"></select>
            </div> 
            <button id="electionSubmit" type="submit" class="btn btn-info">Open Election</button>
            </form>
            `
            let electionOptions = document.querySelector("#electionInput")

            for(election of elections)
                if(election)
                    if(election['isOpen'] == false)
                        electionOptions.innerHTML+=`<option value="${election['electionID']}">${election["position"]} ${election["clubName"]}</option>`
                
            document.forms["openElectionForm"].addEventListener("submit", async function(event){
                event.preventDefault()
                let form = event.target.elements

                electionID = form['electionInput'].value

                data = {
                    "isOpen" : true
                }

                let response = await sendRequest(`/api/elections/${electionID}`, "PUT", data)
                event.target.reset()

                if("error" in response){
                    updateToastContent("Open Election", `${response["error"]}`)
                } else {
                    updateToastContent("Close Election", `Election opened successfully!`)
                    openElection()
                }
            })
        } else {
                content.innerHTML = `
                <div class="col-sm-12 mt-3 text-center text-white">
                    <h5>No Closed Elections</h5>
                    <p>Sorry, but you need to be a manager of an election to open an election.</p>
                </div>
                `
        }
    }
}

async function addCandidate(){
    let content=document.querySelector('#candidate')

    content.innerHTML+=
    `
        <div class="form-group" id="candidate">
        <label for="nameInput" class="text-white">Candidate Name</label>
          <input type="text" class="form-control" placeholder="First Name">
          <input type="text" class="form-control mt-3" placeholder="Last Name">
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

    let response = await sendRequest(`/api/elections`, "POST", data)
    event.target.reset()

    if("error" in response){
        updateToastContent("Add Election", `${response["error"]}`)
    } else {
        updateToastContent("Add Election", "Election successfully added!")
        createElection()
    }
}

function main(){
    document.forms["signUpForm"].addEventListener("submit", signUp)
    document.forms["loginForm"].addEventListener("submit", login)
    document.querySelector("#club-tab").addEventListener("click", getAllClubs)
    document.querySelector("#myClubs-tab").addEventListener("click", getAllMyClubs)
    document.querySelector("#activeElections-tab").addEventListener("click", getAllMyActiveElections)
    document.querySelector("#manageElections-tab").addEventListener("click", displayElectionsManager)
    document.querySelector("#pastElections-tab").addEventListener("click", getMyPastElections)
    let logoutButton = document.querySelector("#logoutButton")
    logoutButton.addEventListener("click", logout)
    $('.toast').toast({"delay" : 3000})
    determineSessionContext()
    getAllClubs()
}

document.addEventListener('DOMContentLoaded', main)