/*=============== SHOW MENU ===============*/
const navMenu = document.getElementById('nav-menu'),
      navToggle = document.getElementById('nav-toggle'),
      navClose = document.getElementById('nav-close')

/* Menu show */
navToggle.addEventListener('click', () =>{
   navMenu.classList.add('show-menu')
})

/* Menu hidden */
navClose.addEventListener('click', () =>{
   navMenu.classList.remove('show-menu')
})

/*=============== Profile management form ===============*/
const profile = document.getElementById('profile'),
      profileBtn = document.getElementById('login-btn'),
      profileClose = document.getElementById('profile-close')

/* Profile show */
profileBtn.addEventListener('click', () =>{
   profile.classList.add('show-search')
})

/* Profile hidden */
profileClose.addEventListener('click', () =>{
   profile.classList.remove('show-search')
})

/*=============== SEARCH ===============*/
const search = document.getElementById('search'),
      searchBtn = document.getElementById('search-btn'),
      searchClose = document.getElementById('search-close')

/* Search show */
searchBtn.addEventListener('click', () =>{
   search.classList.add('show-search')
})

/* Search hidden */
searchClose.addEventListener('click', () =>{
   search.classList.remove('show-search')
})