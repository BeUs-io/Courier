'use strict';

/* ===== Enable Bootstrap Popover (on element  ====== */

var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="popover"]'))
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
  return new bootstrap.Popover(popoverTriggerEl);
})

/* ==== Enable Bootstrap Alert ====== */
var alertList = document.querySelectorAll('.alert')
alertList.forEach(function (alert) {
  new bootstrap.Alert(alert);
});

/* ===== Responsive sidebar ====== */
var sidebarToggler = document.getElementById('sidebar-toggler');
var sidebar = document.getElementById('d-sidebar');
var sidebarDrop = document.getElementById('sidebar-drop');
var sidebarClose = document.getElementById('sidebar-close');
var body = document.getElementById('d-body');

window.addEventListener('load', function(){
	responsivesidebar(); 
});

window.addEventListener('resize', function(){
	responsivesidebar(); 
});

function responsivesidebar() {
    let w = window.innerWidth;
	if(w >= 1200) {
		sidebar.classList.remove('sidebar-hidden');
		sidebar.classList.add('sidebar-visible');
	} else {
	    sidebar.classList.remove('sidebar-visible');
		sidebar.classList.add('sidebar-hidden');
	}
};

sidebarToggler.addEventListener('click', () => {
	if (sidebar.classList.contains('sidebar-visible')) {
		sidebar.classList.remove('sidebar-visible');
		sidebar.classList.add('sidebar-hidden');
	} else {
		sidebar.classList.remove('sidebar-hidden');
		sidebar.classList.add('sidebar-visible');
	}
});

sidebarClose.addEventListener('click', (e) => {
	e.preventDefault();
	sidebarToggler.click();
});
sidebarDrop.addEventListener('click', (e) => {
	sidebarToggler.click();
});
/* ====== Enable Bootstrap tooltips everywhere ======= */

var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
	return new bootstrap.Tooltip(tooltipTriggerEl)
})
