"""Plotly Dash HTML layout override."""

html_layout = """
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta content="IE=edge" http-equiv="X-UA-Compatible">
  <meta content="width=device-width,initial-scale=1" name="viewport">
  <meta content="description" name="description">
  <meta name="google" content="notranslate" />
  <meta content="Mashup templates have been developped by Orson.io team" name="author">

  <!-- Disable tap highlight on IE -->
  <meta name="msapplication-tap-highlight" content="no">
  <link rel="apple-touch-icon" sizes="180x180" href="./assets/apple-icon-180x180.png">
  <title>My-Rights</title>
  <link rel="stylesheet" type= "text/css" href="assets/dash.css">
  <link rel="shortcut icon" type="image/x-icon" href="assets/favicon.ico">   
</head>

<body class="">
<div id="site-border-left"></div>
<div id="site-border-right"></div>
<div id="site-border-top"></div>
<div id="site-border-bottom"></div>
 <!-- Add your content of header -->
<header>
  <nav class="navbar  navbar-fixed-top navbar-default" aria-label="Main">
    <div class="container">
        <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapse" aria-expanded="false">
          <span class="sr-only">Toggle navigation</span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
        </button>

      <div class="collapse navbar-collapse" id="navbar-collapse" aria-label="Main">
        <ul class="nav navbar-nav">
          <li><a href="/" title="">Home</a></li>
          <li><a href="/prediction" title="">1 : <b>Prediction</b></a></li>
          <li><a href="/visualisation" title="">2 : <b>Data Visualisation</b></a></li>
          <li><a href="/search" title="">3 : <b>Text Search</b></a></li>
          <li><a href="/about" title="">About</a></li>
        </ul>

      </div>
    </div>
  </nav>
</header>

<div class="section-container">
  <div class="container">
    <div class="row">
        <div class="col-xs-12">
          <div class="section-container-spacer text-center">
            <h2>2 : Data Visualisation</h2>
          </div>
        </div>
    </div>
    <div class="row">
        <div class="col-xs-10 col-xs-offset-1 col-xs-1">
          <div class="section-container-spacer text-center">
                <h3 class="border-line" style="margin-top:0px;">Instructions</h3>
                <p style="text-align: justify; font-size: 16;">Use the boxes on the left to select the relevant information you want to
                filter all cases by. Once you've made your selections, click the 'Select' button. You'll then see a list of all the cases 
                that match your criteria at the bottom of the page. To download a file that contains all of these cases, use the 'Export' button.
                </p>
                </br>
                <p >If you would like further information regarding the definitions of the terms in the selection criteria please go to the 'Important definitions' section within the
                <a href="/about#collapsible-trigger-definitions">About</a> page.</p>
                </br>
                <p>
                <b>Please note that the selection currently being used is for example purposes.</b>
                </p>
          </div>
        </div>
    </div>    
    {%app_entry%}
  </div>
</div>
</body>
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</html>
"""