// script.js

function toggleMode() {
  var body = document.getElementsByTagName('body')[0];
  body.classList.toggle('dark-mode');
}

function showAbstract(button) {
    var abstractDiv = button.nextElementSibling;
    if (abstractDiv.style.display === "none") {
        var pubmedId = button.parentElement.querySelector(".pubmed-id").innerText;
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    var abstract = response.abstract;
                    abstractDiv.innerHTML = "";
                    if (abstract) {
                        abstractDiv.innerHTML = "<h3>Abstract</h3><p>" + abstract + "</p>";
                    } else {
                        abstractDiv.innerHTML = "<p>Abstract Not Found</p>";
                    }
                    abstractDiv.style.display = "block";
                } else {
                    abstractDiv.innerHTML = "<p>Error fetching abstract</p>";
                    abstractDiv.style.display = "block";
                }
            }
        };
        xhr.open("GET", "/abstract/" + pubmedId, true);
        xhr.send();
    } else {
        abstractDiv.style.display = "none";
    }
}