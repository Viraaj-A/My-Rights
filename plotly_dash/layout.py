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
  <link rel="stylesheet" type= "text/css" href="assets/main.css">

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
          <li><a href="/" title="">1 : Home</a></li>
          <li><a href="/questionnaire" title="">2 : Questionnaire</a></li>
          <li><a href="/visualisation.html" title="">3 : Data Visualisation</a></li>
          <li><a href="/search" title="">4 : Text Search</a></li>
          <li><a href="/about.html" title="">5 : About</a></li>
        </ul>
      </div>
    </div>
  </nav>
</header>

<div class="section-container">
  <div class="container">
    {%app_entry%}
  </div>
</div>

<footer class="footer-container text-center">
  <div class="container">
    <div class="row">
      <div class="col-xs-12">
        <p>[INSERT LOGO REQUIREMENTS]<a href="" title="Beautiful Free Images">[INSERT LOGO REQUIREMENTS]</a></p>
      </div>
    </div>
  </div>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</html>
"""