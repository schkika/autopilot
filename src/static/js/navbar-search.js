let typingTimer;        
let typeInterval = 500; // Half a second
let searchInput = document.getElementById('searchbox');

searchInput.addEventListener('keyup', () => {
clearTimeout(typingTimer);
typingTimer = setTimeout(liveSearch, typeInterval);
});

function liveSearch() {
const textinputs = document.getElementsByClassName('card')
let search_query = document.getElementById("searchbox").value;
for (var i = 0; i < textinputs.length; i++) {
// If the text is within the card...
if(textinputs[i].innerText.toLowerCase()
  // ...and the text matches the search query...
  .includes(search_query.toLowerCase())) {
    // ...remove the `.is-hidden` class.
  if(textinputs[i].parentNode.tagName.toLowerCase() === 'a'){
    textinputs[i].parentNode.classList.remove("hidden");
  } else {
    textinputs[i].classList.remove("hidden");
  }
} else {
  // Otherwise, add the class.
  if(textinputs[i].parentNode.tagName.toLowerCase() === 'a'){
    textinputs[i].parentNode.classList.add("hidden");
  } else {
    textinputs[i].classList.add("hidden");
  }
}
}
}