/**
=========================================================================
=========================================================================
Template Name: Buzztia - Admin Template
Author: Jkamilo Lab
Support: https://buzztia.com
File: themes.js
Description:  this file will contains overall theme setup and handle
              behavior of live custumizer like Dark/Light, LTR/RTL,
              preset color, theme layout, theme contarast etc.
=========================================================================
=========================================================================
*/

'use strict';

var rtl_flag = false;
var dark_flag = false;

document.addEventListener('DOMContentLoaded', function () {
  if (typeof Storage !== 'undefined') {
    // Initialize layout from localStorage
    const savedTheme = localStorage.getItem('layout') || 'light';
    layout_change(savedTheme);

    // Initialize RTL from localStorage
    const savedRtl = localStorage.getItem('rtl');
    if (savedRtl) {
      layout_rtl_change(savedRtl);
    }
  }

  // Add RTL toggle listener
  const rtlToggle = document.getElementById('rtl-toggle');
  if (rtlToggle) {
    rtlToggle.addEventListener('click', function(e) {
      e.preventDefault();
      const newRtlValue = (!rtl_flag).toString();
      localStorage.setItem('rtl', newRtlValue);
      layout_rtl_change(newRtlValue);
    });
  }

  // Add theme toggle listener
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function(e) {
      e.preventDefault();
      const newTheme = dark_flag ? 'light' : 'dark';
      localStorage.setItem('layout', newTheme);
      layout_change(newTheme);
    });
  }
});

function layout_change_default() {
  // Determine the initial theme based on system preferences
  let darkLayout = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  layout_change(darkLayout); // Apply the selected layout

  // Activate the "default" layout button, if it exists
  const defaultBtn = document.querySelector('.theme-layout .btn[data-value="default"]');
  if (defaultBtn) {
    defaultBtn.classList.add('active');
  }

  // Listen for changes in the user's system color scheme and update the layout accordingly
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (event) => {
    darkLayout = event.matches ? 'dark' : 'light';
    layout_change(darkLayout); // Apply the new layout when the preference changes
  });
}

// dark switch mode
function dark_mode() {
  const darkModeToggle = document.getElementById('dark-mode');

  // Ensure the element exists before proceeding
  if (!darkModeToggle) return;

  // Toggle between dark and light modes based on the checkbox status
  const mode = darkModeToggle.checked ? 'dark' : 'light';
  layout_change(mode);
}

// preset color
document.addEventListener('DOMContentLoaded', function () {
  const presetColors = document.querySelectorAll('.preset-color > a');
  if (presetColors.length) {
    presetColors.forEach((colorElement) => {
      colorElement.addEventListener('click', function (event) {
        let targetElement = event.target;

        // Traverse up to find the correct clickable element
        if (targetElement.tagName === 'SPAN') {
          targetElement = targetElement.parentNode;
        } else if (targetElement.tagName === 'IMG') {
          targetElement = targetElement.closest('a');
        }

        const presetValue = targetElement.getAttribute('data-value');
        preset_change(presetValue);
      });
    });
  }

  // Initialize SimpleBar if .pct-body exists
  const pctBody = document.querySelector('.pct-body');
  if (pctBody) {
    new SimpleBar(pctBody);
  }

  // Handle layout reset
  const layoutResetBtn = document.querySelector('#layoutreset');
  if (layoutResetBtn) {
    layoutResetBtn.addEventListener('click', () => location.reload());
  }

  // Select all layout buttons
  const layoutButtons = document.querySelectorAll('.theme-layout .btn');

  // Add click event listeners to each layout button
  layoutButtons.forEach((button) => {
    button.addEventListener('click', (event) => {
      event.stopPropagation(); // Prevent event bubbling

      // Get the target element, accounting for nested <span> clicks
      let target = event.target;
      while (target.tagName === 'SPAN') {
        target = target.parentNode;
      }

      // Determine the layout value and store it in localStorage
      const layoutValue = target.getAttribute('data-value') === 'true' ? 'light' : 'dark';
      localStorage.setItem('layout', layoutValue);
    });
  });
});

function font_change(name) {
  const fontUrls = {
    Roboto: 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap',
    Poppins: 'https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700&display=swap',
    Inter: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap'
  };

  // Set the font stylesheet link
  const src = fontUrls[name] || '';
  document.querySelector('#main-font-link').setAttribute('href', src);

  // Apply the font family to the body
  document.body.style.fontFamily = `"${name}", sans-serif`;

  // Update the font selection radio button, if the off-canvas control exists
  const control = document.querySelector('.pct-offcanvas');
  if (control) {
    const radio = document.querySelector(`#layoutfont${name}`);
    if (radio) {
      radio.checked = true;
    }
  }
}

function layout_caption_change(value) {
  const isActive = value === 'true';

  // Update the body attribute based on the selected value
  document.body.setAttribute('data-pc-sidebar-caption', isActive ? 'true' : 'false');

  // Find and deactivate the currently active button, if any
  const activeButton = document.querySelector('.theme-nav-caption .btn.active');
  if (activeButton) {
    activeButton.classList.remove('active');
  }

  // Activate the new button based on the selected value
  const targetButton = document.querySelector(`.theme-nav-caption .btn[data-value='${value}']`);
  if (targetButton) {
    targetButton.classList.add('active');
  }
}

function preset_change(value) {
  const body = document.querySelector('body');
  const control = document.querySelector('.pct-offcanvas');

  // Set the 'data-pc-preset' attribute on the body
  body.setAttribute('data-pc-preset', value);

  // Update active state in the UI if control exists
  if (control) {
    const activeElement = document.querySelector('.preset-color > a.active');
    const newActiveElement = document.querySelector(`.preset-color > a[data-value='${value}']`);

    if (activeElement) {
      activeElement.classList.remove('active');
    }
    if (newActiveElement) {
      newActiveElement.classList.add('active');
    }
  }
}

function layout_rtl_change(value) {
  const body = document.querySelector('body');
  const html = document.querySelector('html');

  rtl_flag = value === 'true';

  if (rtl_flag) {
    body.setAttribute('data-pc-direction', 'rtl');
    html.setAttribute('dir', 'rtl');
    html.setAttribute('lang', 'ar');
  } else {
    body.setAttribute('data-pc-direction', 'ltr');
    html.removeAttribute('dir');
    html.setAttribute('lang', 'en');
  }

  // Update localStorage
  localStorage.setItem('rtl', rtl_flag.toString());
}

function layout_change(layout) {
  const isDark = layout === 'dark';

  // Update body and html attributes
  document.documentElement.setAttribute('data-bs-theme', layout);
  document.documentElement.setAttribute('data-pc-theme', layout);
  document.body.setAttribute('data-pc-theme', layout);

  // Store the theme preference
  localStorage.setItem('layout', layout);

  // Update dark_flag
  dark_flag = isDark;

  // Update theme toggle icon if it exists
  const themeToggleIcon = document.querySelector('#theme-toggle i');
  if (themeToggleIcon) {
    themeToggleIcon.className = isDark ? 'ti ti-sun' : 'ti ti-moon';
  }

  // Update theme toggle text if it exists
  const themeToggleText = document.querySelector('.theme-toggle-text');
  if (themeToggleText) {
    themeToggleText.textContent = isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode';
  }

  // Dispatch a custom event that we can listen to for theme changes
  const event = new CustomEvent('themeChanged', { detail: { theme: layout } });
  document.dispatchEvent(event);
}

// Add this new function to initialize theme on page load
function initializeTheme() {
  const savedTheme = localStorage.getItem('layout') || 'light';
  layout_change(savedTheme);
}

// Call initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  initializeTheme();
});

function change_box_container(value) {
  const content = document.querySelector('.pc-content');
  const footerWrapper = document.querySelector('.footer-wrapper');
  const activeControl = document.querySelector('.theme-container > a.active');

  // Check if content and footer elements exist
  if (content && footerWrapper) {
    const isBoxed = value === 'true';

    // Helper function to toggle class names
    function toggleContainer(isBoxed) {
      if (isBoxed) {
        content.classList.add('container');
        footerWrapper.classList.add('container');
        footerWrapper.classList.remove('container-fluid');
      } else {
        content.classList.remove('container');
        footerWrapper.classList.remove('container');
        footerWrapper.classList.add('container-fluid');
      }
    }

    toggleContainer(isBoxed);

    // Update active button class
    if (activeControl) {
      activeControl.classList.remove('active');
      const newActive = document.querySelector(`.theme-container > a[data-value='${value}']`);
      if (newActive) {
        newActive.classList.add('active');
      }
    }
  }
}
