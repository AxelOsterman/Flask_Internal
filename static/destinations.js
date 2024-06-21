/*=============== Show Filters ===============*/
const filter = document.getElementById('filter'),
      filterDiv = document.getElementById('filterdiv');
let active = false

/* Show filter / Hide Filter */
filter.addEventListener('click', () =>{
   if (active){
      filterDiv.classList.remove('show-filter')
      active = false
   } else{
      filterDiv.classList.add('show-filter')
      active = true
   }
})