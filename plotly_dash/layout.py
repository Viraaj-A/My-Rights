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

  <!-- Disable tap highlight on IE -->
  <meta name="msapplication-tap-highlight" content="no">
  <link rel="apple-touch-icon" sizes="180x180" href="./assets/apple-icon-180x180.png">
  <link href="./assets/favicon.ico" rel="icon">
  <title>My-Rights</title>
  <link rel="stylesheet" type= "text/css" href="assets/dash.css">
  <link rel="shortcut icon" href="{{ url_for('static', filename='assets/images/favicon.ico') }}">
</head>
    
<body class="">
<div id="site-border-left"></div>
<div id="site-border-right"></div>
<div id="site-border-top"></div>
<div id="site-border-bottom"></div>
 <!-- Add your content of header -->
<header>
  <nav class="navbar  navbar-fixed-top navbar-default">
    <div class="container">
        <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapse" aria-expanded="false">
          <span class="sr-only">Toggle navigation</span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
        </button>

      <div class="collapse navbar-collapse" id="navbar-collapse">
        <ul class="nav navbar-nav ">
          <li><a href="/" title="">Home</a></li>
          <li><a href="/questionnaire" title="">1 : Questionnaire</a></li>
          <li><a href="/visualisation" title="">2 : Data Visualisation</a></li>
          <li><a href="/search" title="">3 : Text Search</a></li>
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
            <h1 class="h2">2 : Data Visualisation</h1>
          </div>
        </div>
    </div>
    <div class="row">
        <div class="col-xs-10 col-xs-offset-1 col-xs-1">
          <div class="section-container-spacer text-center">
                <p style='font-size:1.2em'><b>INSTRUCTIONS:</b></p>
                <p style="text-align: justify"><b>Use the boxes on the left to select the relevant information you want to
                filter all cases by. After making your selection click the 'Select' Button. 
                Scroll down to the bottom of the page where you can see all relevant cases. 
                Use the 'Export' button to download a file that contains all the relevant cases. 
                </b></p>
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