const parentElement = document.getElementById('parent');

parentElement.onmouseover = e => {
  e.target.innerHTML = e.target.innerText.replace(/([\w]+)/g, '<span>$1</span>');
};