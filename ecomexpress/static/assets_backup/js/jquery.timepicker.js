  


<!DOCTYPE html>
<html>
  <head prefix="og: http://ogp.me/ns# fb: http://ogp.me/ns/fb# githubog: http://ogp.me/ns/fb/githubog#">
    <meta charset='utf-8'>
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>jquery-timepicker/jquery.timepicker.js at master · jonthornton/jquery-timepicker</title>
    <link rel="search" type="application/opensearchdescription+xml" href="/opensearch.xml" title="GitHub" />
    <link rel="fluid-icon" href="https://github.com/fluidicon.png" title="GitHub" />
    <link rel="apple-touch-icon-precomposed" sizes="57x57" href="apple-touch-icon-114.png" />
    <link rel="apple-touch-icon-precomposed" sizes="114x114" href="apple-touch-icon-114.png" />
    <link rel="apple-touch-icon-precomposed" sizes="72x72" href="apple-touch-icon-144.png" />
    <link rel="apple-touch-icon-precomposed" sizes="144x144" href="apple-touch-icon-144.png" />
    <meta name="msapplication-TileImage" content="/windows-tile.png">
    <meta name="msapplication-TileColor" content="#ffffff">

    
    
    <link rel="icon" type="image/x-icon" href="/favicon.ico" />

    <meta content="authenticity_token" name="csrf-param" />
<meta content="OqNmtOoIMeB+xelETDZnZv+T/zhcyAnlpXA7mztFo8w=" name="csrf-token" />

    <link href="https://a248.e.akamai.net/assets.github.com/assets/github-dd95960936fd09bc718d54eac1f1683ed3376505.css" media="screen" rel="stylesheet" type="text/css" />
    <link href="https://a248.e.akamai.net/assets.github.com/assets/github2-afd2b1fd12ec1081f0742d6bcdff732bc29e17ee.css" media="screen" rel="stylesheet" type="text/css" />
    


    <script src="https://a248.e.akamai.net/assets.github.com/assets/frameworks-57542e0cba19d068168099f287c117efa142863c.js" type="text/javascript"></script>
    <script src="https://a248.e.akamai.net/assets.github.com/assets/github-87dddfbca2bfbbb5011e09d2d2c7e49e64af16b8.js" type="text/javascript"></script>
    

      <link rel='permalink' href='/jonthornton/jquery-timepicker/blob/9aa22d7c8223e786a36582ac1095b07b59a0bd43/jquery.timepicker.js'>
    <meta property="og:title" content="jquery-timepicker"/>
    <meta property="og:type" content="githubog:gitrepository"/>
    <meta property="og:url" content="https://github.com/jonthornton/jquery-timepicker"/>
    <meta property="og:image" content="https://secure.gravatar.com/avatar/9eca28d052c317aaa02e676d7b644e48?s=420&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png"/>
    <meta property="og:site_name" content="GitHub"/>
    <meta property="og:description" content="jquery-timepicker - A jQuery timepicker plugin inspired by Google Calendar."/>

    <meta name="description" content="jquery-timepicker - A jQuery timepicker plugin inspired by Google Calendar." />

  <link href="https://github.com/jonthornton/jquery-timepicker/commits/master.atom" rel="alternate" title="Recent Commits to jquery-timepicker:master" type="application/atom+xml" />

  </head>


  <body class="logged_in page-blob windows vis-public env-production ">
    <div id="wrapper">

      

      

      


        <div class="header header-logged-in true">
          <div class="container clearfix">

            <a class="header-logo-blacktocat" href="https://github.com/">
  <span class="mega-icon mega-icon-blacktocat"></span>
</a>

            <div class="divider-vertical"></div>

              <a href="/notifications" class="notification-indicator tooltipped downwards" title="You have no unread notifications">
    <span class="mail-status all-read"></span>
  </a>
  <div class="divider-vertical"></div>


              
  <div class="topsearch command-bar-activated">
    <form accept-charset="UTF-8" action="/search" class="command_bar_form" id="top_search_form" method="get">
  <a href="/search/advanced" class="advanced-search tooltipped downwards command-bar-search" id="advanced_search" title="Advanced search"><span class="mini-icon mini-icon-advanced-search "></span></a>

  <input type="text" name="q" id="command-bar" placeholder="Search or type a command" tabindex="1" data-username="crazysirius" autocapitalize="off">

  <span class="mini-icon help tooltipped downwards" title="Show command bar help">
    <span class="mini-icon mini-icon-help"></span>
  </span>

  <input type="hidden" name="ref" value="commandbar">

  <div class="divider-vertical"></div>
</form>



    <ul class="top-nav">
        <li class="explore"><a href="https://github.com/explore">Explore</a></li>
        <li><a href="https://gist.github.com">Gist</a></li>
        <li><a href="/blog">Blog</a></li>
      <li><a href="http://help.github.com">Help</a></li>
    </ul>
  </div>


            

  
    <ul id="user-links">
      <li>
        <a href="https://github.com/crazysirius" class="name">
          <img height="20" src="https://secure.gravatar.com/avatar/887b70636d169283e47fb851e3098470?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /> crazysirius
        </a>
      </li>
      <li>
        <a href="/new" id="new_repo" class="tooltipped downwards" title="Create a new repo">
          <span class="mini-icon mini-icon-create"></span>
        </a>
      </li>
      <li>
        <a href="/settings/profile" id="account_settings"
          class="tooltipped downwards"
          title="Account settings ">
          <span class="mini-icon mini-icon-account-settings"></span>
        </a>
      </li>
      <li>
          <a href="/logout" data-method="post" id="logout" class="tooltipped downwards" title="Sign out">
            <span class="mini-icon mini-icon-logout"></span>
          </a>
      </li>
    </ul>



            
          </div>
        </div>


      

      


            <div class="site hfeed" itemscope itemtype="http://schema.org/WebPage">
      <div class="hentry">
        
        <div class="pagehead repohead instapaper_ignore readability-menu">
          <div class="container">
            <div class="title-actions-bar">
              


                  <ul class="pagehead-actions">

          <li class="subscription">
              <form accept-charset="UTF-8" action="/notifications/subscribe" data-autosubmit="true" data-remote="true" method="post"><div style="margin:0;padding:0;display:inline"><input name="authenticity_token" type="hidden" value="OqNmtOoIMeB+xelETDZnZv+T/zhcyAnlpXA7mztFo8w=" /></div>  <input id="repository_id" name="repository_id" type="hidden" value="2753802" />
  <div class="context-menu-container js-menu-container js-context-menu">
    <span class="minibutton switcher bigger js-menu-target">
      <span class="js-context-button">
          <span class="mini-icon mini-icon-watching"></span>Watch
      </span>
    </span>

    <div class="context-pane js-menu-content">
      <a href="javascript:;" class="close js-menu-close"><span class="mini-icon mini-icon-remove-close"></span></a>
      <div class="context-title">Notification status</div>

      <div class="context-body pane-selector">
        <ul class="js-navigation-container">
          <li class="selector-item js-navigation-item js-navigation-target selected">
            <span class="mini-icon mini-icon-confirm"></span>
            <label>
              <input checked="checked" id="do_included" name="do" type="radio" value="included" />
              <h4>Not watching</h4>
              <p>You will only receive notifications when you participate or are mentioned.</p>
            </label>
            <span class="context-button-text js-context-button-text">
              <span class="mini-icon mini-icon-watching"></span>
              Watch
            </span>
          </li>
          <li class="selector-item js-navigation-item js-navigation-target ">
            <span class="mini-icon mini-icon-confirm"></span>
            <label>
              <input id="do_subscribed" name="do" type="radio" value="subscribed" />
              <h4>Watching</h4>
              <p>You will receive all notifications for this repository.</p>
            </label>
            <span class="context-button-text js-context-button-text">
              <span class="mini-icon mini-icon-unwatch"></span>
              Unwatch
            </span>
          </li>
          <li class="selector-item js-navigation-item js-navigation-target ">
            <span class="mini-icon mini-icon-confirm"></span>
            <label>
              <input id="do_ignore" name="do" type="radio" value="ignore" />
              <h4>Ignored</h4>
              <p>You will not receive notifications for this repository.</p>
            </label>
            <span class="context-button-text js-context-button-text">
              <span class="mini-icon mini-icon-mute"></span>
              Stop ignoring
            </span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</form>
          </li>

          <li class="js-toggler-container js-social-container starring-container ">
            <a href="/jonthornton/jquery-timepicker/unstar" class="minibutton js-toggler-target starred" data-remote="true" data-method="post" rel="nofollow">
              <span class="mini-icon mini-icon-star"></span>Unstar
            </a><a href="/jonthornton/jquery-timepicker/star" class="minibutton js-toggler-target unstarred" data-remote="true" data-method="post" rel="nofollow">
              <span class="mini-icon mini-icon-star"></span>Star
            </a><a class="social-count js-social-count" href="/jonthornton/jquery-timepicker/stargazers">440</a>
          </li>

              <li><a href="/jonthornton/jquery-timepicker/fork" class="minibutton js-toggler-target fork-button lighter" rel="nofollow" data-method="post"><span class="mini-icon mini-icon-fork"></span>Fork</a><a href="/jonthornton/jquery-timepicker/network" class="social-count">53</a>
              </li>


    </ul>

              <h1 itemscope itemtype="http://data-vocabulary.org/Breadcrumb" class="entry-title public">
                <span class="repo-label"><span>public</span></span>
                <span class="mega-icon mega-icon-public-repo"></span>
                <span class="author vcard">
                  <a href="/jonthornton" class="url fn" itemprop="url" rel="author">
                  <span itemprop="title">jonthornton</span>
                  </a></span> /
                <strong><a href="/jonthornton/jquery-timepicker" class="js-current-repository">jquery-timepicker</a></strong>
              </h1>
            </div>

            

  <ul class="tabs">
    <li><a href="/jonthornton/jquery-timepicker" class="selected" highlight="repo_sourcerepo_downloadsrepo_commitsrepo_tagsrepo_branches">Code</a></li>
    <li><a href="/jonthornton/jquery-timepicker/network" highlight="repo_network">Network</a></li>
    <li><a href="/jonthornton/jquery-timepicker/pulls" highlight="repo_pulls">Pull Requests <span class='counter'>0</span></a></li>

      <li><a href="/jonthornton/jquery-timepicker/issues" highlight="repo_issues">Issues <span class='counter'>0</span></a></li>

      <li><a href="/jonthornton/jquery-timepicker/wiki" highlight="repo_wiki">Wiki</a></li>


    <li><a href="/jonthornton/jquery-timepicker/graphs" highlight="repo_graphsrepo_contributors">Graphs</a></li>


  </ul>
  
<div class="tabnav">

  <span class="tabnav-right">
    <ul class="tabnav-tabs">
      <li><a href="/jonthornton/jquery-timepicker/tags" class="tabnav-tab" highlight="repo_tags">Tags <span class="counter ">1</span></a></li>
      <li><a href="/jonthornton/jquery-timepicker/downloads" class="tabnav-tab" highlight="repo_downloads">Downloads <span class="counter blank">0</span></a></li>
    </ul>
    
  </span>

  <div class="tabnav-widget scope">


    <div class="context-menu-container js-menu-container js-context-menu">
      <a href="#"
         class="minibutton bigger switcher js-menu-target js-commitish-button btn-branch repo-tree"
         data-hotkey="w"
         data-ref="master">
         <span><em class="mini-icon mini-icon-branch"></em><i>branch:</i> master</span>
      </a>

      <div class="context-pane commitish-context js-menu-content">
        <a href="javascript:;" class="close js-menu-close"><span class="mini-icon mini-icon-remove-close"></span></a>
        <div class="context-title">Switch branches/tags</div>
        <div class="context-body pane-selector commitish-selector js-navigation-container">
          <div class="filterbar">
            <input type="text" id="context-commitish-filter-field" class="js-navigation-enable js-filterable-field" placeholder="Filter branches/tags">
            <ul class="tabs">
              <li><a href="#" data-filter="branches" class="selected">Branches</a></li>
                <li><a href="#" data-filter="tags">Tags</a></li>
            </ul>
          </div>

          <div class="js-filter-tab js-filter-branches">
            <div data-filterable-for="context-commitish-filter-field" data-filterable-type=substring>
                <div class="commitish-item branch-commitish selector-item js-navigation-item js-navigation-target ">
                  <span class="mini-icon mini-icon-confirm"></span>
                  <h4>
                      <a href="/jonthornton/jquery-timepicker/blob/auto-format/jquery.timepicker.js" class="js-navigation-open" data-name="auto-format" rel="nofollow">auto-format</a>
                  </h4>
                </div>
                <div class="commitish-item branch-commitish selector-item js-navigation-item js-navigation-target ">
                  <span class="mini-icon mini-icon-confirm"></span>
                  <h4>
                      <a href="/jonthornton/jquery-timepicker/blob/bootstrap-style/jquery.timepicker.js" class="js-navigation-open" data-name="bootstrap-style" rel="nofollow">bootstrap-style</a>
                  </h4>
                </div>
                <div class="commitish-item branch-commitish selector-item js-navigation-item js-navigation-target ">
                  <span class="mini-icon mini-icon-confirm"></span>
                  <h4>
                      <a href="/jonthornton/jquery-timepicker/blob/gh-pages/jquery.timepicker.js" class="js-navigation-open" data-name="gh-pages" rel="nofollow">gh-pages</a>
                  </h4>
                </div>
                <div class="commitish-item branch-commitish selector-item js-navigation-item js-navigation-target selected">
                  <span class="mini-icon mini-icon-confirm"></span>
                  <h4>
                      <a href="/jonthornton/jquery-timepicker/blob/master/jquery.timepicker.js" class="js-navigation-open" data-name="master" rel="nofollow">master</a>
                  </h4>
                </div>
                <div class="commitish-item branch-commitish selector-item js-navigation-item js-navigation-target ">
                  <span class="mini-icon mini-icon-confirm"></span>
                  <h4>
                      <a href="/jonthornton/jquery-timepicker/blob/none-option/jquery.timepicker.js" class="js-navigation-open" data-name="none-option" rel="nofollow">none-option</a>
                  </h4>
                </div>
            </div>
            <div class="no-results">Nothing to show</div>
          </div>

            <div class="js-filter-tab js-filter-tags " style="display:none">
              <div data-filterable-for="context-commitish-filter-field" data-filterable-type=substring>
                  <div class="commitish-item tag-commitish selector-item js-navigation-item js-navigation-target ">
                    <span class="mini-icon mini-icon-confirm"></span>
                    <h4>
                        <a href="/jonthornton/jquery-timepicker/blob/v1.0.0/jquery.timepicker.js" class="js-navigation-open" data-name="v1.0.0" rel="nofollow">v1.0.0</a>
                    </h4>
                  </div>
              </div>
              <div class="no-results">Nothing to show</div>
            </div>
        </div>
      </div><!-- /.commitish-context-context -->
    </div>
  </div> <!-- /.scope -->

  <ul class="tabnav-tabs">
    <li><a href="/jonthornton/jquery-timepicker" class="selected tabnav-tab" highlight="repo_source">Files</a></li>
    <li><a href="/jonthornton/jquery-timepicker/commits/master" class="tabnav-tab" highlight="repo_commits">Commits</a></li>
    <li><a href="/jonthornton/jquery-timepicker/branches" class="tabnav-tab" highlight="repo_branches" rel="nofollow">Branches <span class="counter ">5</span></a></li>
  </ul>

</div>

  
  
  


            
          </div>
        </div><!-- /.repohead -->

        <div id="js-repo-pjax-container" class="container context-loader-container" data-pjax-container>
          


<!-- blob contrib key: blob_contributors:v21:0eee6a0520571fe94c3f179f53c5f6a4 -->
<!-- blob contrib frag key: views10/v8/blob_contributors:v21:0eee6a0520571fe94c3f179f53c5f6a4 -->

<div id="slider">


    <p title="This is a placeholder element" class="js-history-link-replace hidden"></p>
    <div class="breadcrumb" data-path="jquery.timepicker.js/">
      <span class='bold'><span itemscope="" itemtype="http://data-vocabulary.org/Breadcrumb"><a href="/jonthornton/jquery-timepicker" class="js-slider-breadcrumb" itemscope="url"><span itemprop="title">jquery-timepicker</span></a></span></span> / <strong class="final-path">jquery.timepicker.js</strong> <span class="js-clippy mini-icon mini-icon-clippy " data-clipboard-text="jquery.timepicker.js" data-copied-hint="copied!" data-copy-hint="copy to clipboard"></span>
    </div>

    <a href="/jonthornton/jquery-timepicker/find/master" class="js-slide-to" data-hotkey="t" style="display:none">Show File Finder</a>

      
  <div class="commit file-history-tease" data-path="jquery.timepicker.js/">
    <img class="main-avatar" height="24" src="https://secure.gravatar.com/avatar/d8adec7b8e0610bbc920e2393b70dd7d?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
    <span class="author"><a href="/nervetattoo">nervetattoo</a></span>
    <time class="js-relative-date" datetime="2012-11-26T03:55:30-08:00" title="2012-11-26 03:55:30">November 26, 2012</time>
    <div class="commit-title">
        <a href="/jonthornton/jquery-timepicker/commit/af6f0c115f48264f69b0d9089bfdd83efab840ee" class="message">Close dropdown and blur input field when tapping outside on touch dev…</a>
    </div>

    <div class="participation">
      <p class="quickstat"><a href="#blob_contributors_box" rel="facebox"><strong>10</strong> contributors</a></p>
          <a class="avatar tooltipped downwards" title="jonthornton" href="/jonthornton/jquery-timepicker/commits/master/jquery.timepicker.js?author=jonthornton"><img height="20" src="https://secure.gravatar.com/avatar/9eca28d052c317aaa02e676d7b644e48?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
    <a class="avatar tooltipped downwards" title="nervetattoo" href="/jonthornton/jquery-timepicker/commits/master/jquery.timepicker.js?author=nervetattoo"><img height="20" src="https://secure.gravatar.com/avatar/d8adec7b8e0610bbc920e2393b70dd7d?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
    <a class="avatar tooltipped downwards" title="vinc3m1" href="/jonthornton/jquery-timepicker/commits/master/jquery.timepicker.js?author=vinc3m1"><img height="20" src="https://secure.gravatar.com/avatar/08a61a592de2ae5bf8df7cab54500978?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
    <a class="avatar tooltipped downwards" title="orloffv" href="/jonthornton/jquery-timepicker/commits/master/jquery.timepicker.js?author=orloffv"><img height="20" src="https://secure.gravatar.com/avatar/3b486c3196772f959e12f31877861f5d?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
    <a class="avatar tooltipped downwards" title="philfreo" href="/jonthornton/jquery-timepicker/commits/master/jquery.timepicker.js?author=philfreo"><img height="20" src="https://secure.gravatar.com/avatar/529a6049c4ad4483dbc62add6da06e1a?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
    <a class="avatar tooltipped downwards" title="fojas" href="/jonthornton/jquery-timepicker/commits/master/jquery.timepicker.js?author=fojas"><img height="20" src="https://secure.gravatar.com/avatar/875e0cf39c5ea0b0450ab4f143e72471?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
    <a class="avatar tooltipped downwards" title="elarkin" href="/jonthornton/jquery-timepicker/commits/master/jquery.timepicker.js?author=elarkin"><img height="20" src="https://secure.gravatar.com/avatar/786c7a9a7862195b83a127efcd296a5a?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
    <a class="avatar tooltipped downwards" title="Spoon88" href="/jonthornton/jquery-timepicker/commits/master/jquery.timepicker.js?author=Spoon88"><img height="20" src="https://secure.gravatar.com/avatar/c416e4168644de8fd5cd5cb7935b9a0a?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
    <a class="avatar tooltipped downwards" title="slarti42uk" href="/jonthornton/jquery-timepicker/commits/master/jquery.timepicker.js?author=slarti42uk"><img height="20" src="https://secure.gravatar.com/avatar/ea3f159979003fb70204c0f07b144b57?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
    <a class="avatar tooltipped downwards" title="lodewijk" href="/jonthornton/jquery-timepicker/commits/master/jquery.timepicker.js?author=lodewijk"><img height="20" src="https://secure.gravatar.com/avatar/a347386377e120e3230403d2558c1a0d?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>


    </div>
    <div id="blob_contributors_box" style="display:none">
      <h2>Users on GitHub who have contributed to this file</h2>
      <ul class="facebox-user-list">
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/9eca28d052c317aaa02e676d7b644e48?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/jonthornton">jonthornton</a>
        </li>
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/d8adec7b8e0610bbc920e2393b70dd7d?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/nervetattoo">nervetattoo</a>
        </li>
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/08a61a592de2ae5bf8df7cab54500978?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/vinc3m1">vinc3m1</a>
        </li>
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/3b486c3196772f959e12f31877861f5d?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/orloffv">orloffv</a>
        </li>
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/529a6049c4ad4483dbc62add6da06e1a?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/philfreo">philfreo</a>
        </li>
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/875e0cf39c5ea0b0450ab4f143e72471?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/fojas">fojas</a>
        </li>
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/786c7a9a7862195b83a127efcd296a5a?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/elarkin">elarkin</a>
        </li>
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/c416e4168644de8fd5cd5cb7935b9a0a?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/Spoon88">Spoon88</a>
        </li>
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/ea3f159979003fb70204c0f07b144b57?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/slarti42uk">slarti42uk</a>
        </li>
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/a347386377e120e3230403d2558c1a0d?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/lodewijk">lodewijk</a>
        </li>
      </ul>
    </div>
  </div>


    <div class="frames">
      <div class="frame frame-center" data-path="jquery.timepicker.js/" data-permalink-url="/jonthornton/jquery-timepicker/blob/9aa22d7c8223e786a36582ac1095b07b59a0bd43/jquery.timepicker.js" data-title="jquery-timepicker/jquery.timepicker.js at master · jonthornton/jquery-timepicker · GitHub" data-type="blob">

        <div id="files" class="bubble">
          <div class="file">
            <div class="meta">
              <div class="info">
                <span class="icon"><b class="mini-icon mini-icon-text-file"></b></span>
                <span class="mode" title="File Mode">file</span>
                  <span>654 lines (520 sloc)</span>
                <span>15.326 kb</span>
              </div>
              <ul class="button-group actions">
                  <li>
                        <a class="grouped-button minibutton bigger lighter tooltipped leftwards"
                           title="Clicking this button will automatically fork this project so you can edit the file"
                           href="/jonthornton/jquery-timepicker/edit/master/jquery.timepicker.js"
                           data-method="post" rel="nofollow">Edit</a>
                  </li>
                <li><a href="/jonthornton/jquery-timepicker/raw/master/jquery.timepicker.js" class="minibutton grouped-button bigger lighter" id="raw-url">Raw</a></li>
                  <li><a href="/jonthornton/jquery-timepicker/blame/master/jquery.timepicker.js" class="minibutton grouped-button bigger lighter">Blame</a></li>
                <li><a href="/jonthornton/jquery-timepicker/commits/master/jquery.timepicker.js" class="minibutton grouped-button bigger lighter" rel="nofollow">History</a></li>
              </ul>
            </div>
                <div class="data type-javascript">
      <table cellpadding="0" cellspacing="0" class="lines">
        <tr>
          <td>
            <pre class="line_numbers"><span id="L1" rel="#L1">1</span>
<span id="L2" rel="#L2">2</span>
<span id="L3" rel="#L3">3</span>
<span id="L4" rel="#L4">4</span>
<span id="L5" rel="#L5">5</span>
<span id="L6" rel="#L6">6</span>
<span id="L7" rel="#L7">7</span>
<span id="L8" rel="#L8">8</span>
<span id="L9" rel="#L9">9</span>
<span id="L10" rel="#L10">10</span>
<span id="L11" rel="#L11">11</span>
<span id="L12" rel="#L12">12</span>
<span id="L13" rel="#L13">13</span>
<span id="L14" rel="#L14">14</span>
<span id="L15" rel="#L15">15</span>
<span id="L16" rel="#L16">16</span>
<span id="L17" rel="#L17">17</span>
<span id="L18" rel="#L18">18</span>
<span id="L19" rel="#L19">19</span>
<span id="L20" rel="#L20">20</span>
<span id="L21" rel="#L21">21</span>
<span id="L22" rel="#L22">22</span>
<span id="L23" rel="#L23">23</span>
<span id="L24" rel="#L24">24</span>
<span id="L25" rel="#L25">25</span>
<span id="L26" rel="#L26">26</span>
<span id="L27" rel="#L27">27</span>
<span id="L28" rel="#L28">28</span>
<span id="L29" rel="#L29">29</span>
<span id="L30" rel="#L30">30</span>
<span id="L31" rel="#L31">31</span>
<span id="L32" rel="#L32">32</span>
<span id="L33" rel="#L33">33</span>
<span id="L34" rel="#L34">34</span>
<span id="L35" rel="#L35">35</span>
<span id="L36" rel="#L36">36</span>
<span id="L37" rel="#L37">37</span>
<span id="L38" rel="#L38">38</span>
<span id="L39" rel="#L39">39</span>
<span id="L40" rel="#L40">40</span>
<span id="L41" rel="#L41">41</span>
<span id="L42" rel="#L42">42</span>
<span id="L43" rel="#L43">43</span>
<span id="L44" rel="#L44">44</span>
<span id="L45" rel="#L45">45</span>
<span id="L46" rel="#L46">46</span>
<span id="L47" rel="#L47">47</span>
<span id="L48" rel="#L48">48</span>
<span id="L49" rel="#L49">49</span>
<span id="L50" rel="#L50">50</span>
<span id="L51" rel="#L51">51</span>
<span id="L52" rel="#L52">52</span>
<span id="L53" rel="#L53">53</span>
<span id="L54" rel="#L54">54</span>
<span id="L55" rel="#L55">55</span>
<span id="L56" rel="#L56">56</span>
<span id="L57" rel="#L57">57</span>
<span id="L58" rel="#L58">58</span>
<span id="L59" rel="#L59">59</span>
<span id="L60" rel="#L60">60</span>
<span id="L61" rel="#L61">61</span>
<span id="L62" rel="#L62">62</span>
<span id="L63" rel="#L63">63</span>
<span id="L64" rel="#L64">64</span>
<span id="L65" rel="#L65">65</span>
<span id="L66" rel="#L66">66</span>
<span id="L67" rel="#L67">67</span>
<span id="L68" rel="#L68">68</span>
<span id="L69" rel="#L69">69</span>
<span id="L70" rel="#L70">70</span>
<span id="L71" rel="#L71">71</span>
<span id="L72" rel="#L72">72</span>
<span id="L73" rel="#L73">73</span>
<span id="L74" rel="#L74">74</span>
<span id="L75" rel="#L75">75</span>
<span id="L76" rel="#L76">76</span>
<span id="L77" rel="#L77">77</span>
<span id="L78" rel="#L78">78</span>
<span id="L79" rel="#L79">79</span>
<span id="L80" rel="#L80">80</span>
<span id="L81" rel="#L81">81</span>
<span id="L82" rel="#L82">82</span>
<span id="L83" rel="#L83">83</span>
<span id="L84" rel="#L84">84</span>
<span id="L85" rel="#L85">85</span>
<span id="L86" rel="#L86">86</span>
<span id="L87" rel="#L87">87</span>
<span id="L88" rel="#L88">88</span>
<span id="L89" rel="#L89">89</span>
<span id="L90" rel="#L90">90</span>
<span id="L91" rel="#L91">91</span>
<span id="L92" rel="#L92">92</span>
<span id="L93" rel="#L93">93</span>
<span id="L94" rel="#L94">94</span>
<span id="L95" rel="#L95">95</span>
<span id="L96" rel="#L96">96</span>
<span id="L97" rel="#L97">97</span>
<span id="L98" rel="#L98">98</span>
<span id="L99" rel="#L99">99</span>
<span id="L100" rel="#L100">100</span>
<span id="L101" rel="#L101">101</span>
<span id="L102" rel="#L102">102</span>
<span id="L103" rel="#L103">103</span>
<span id="L104" rel="#L104">104</span>
<span id="L105" rel="#L105">105</span>
<span id="L106" rel="#L106">106</span>
<span id="L107" rel="#L107">107</span>
<span id="L108" rel="#L108">108</span>
<span id="L109" rel="#L109">109</span>
<span id="L110" rel="#L110">110</span>
<span id="L111" rel="#L111">111</span>
<span id="L112" rel="#L112">112</span>
<span id="L113" rel="#L113">113</span>
<span id="L114" rel="#L114">114</span>
<span id="L115" rel="#L115">115</span>
<span id="L116" rel="#L116">116</span>
<span id="L117" rel="#L117">117</span>
<span id="L118" rel="#L118">118</span>
<span id="L119" rel="#L119">119</span>
<span id="L120" rel="#L120">120</span>
<span id="L121" rel="#L121">121</span>
<span id="L122" rel="#L122">122</span>
<span id="L123" rel="#L123">123</span>
<span id="L124" rel="#L124">124</span>
<span id="L125" rel="#L125">125</span>
<span id="L126" rel="#L126">126</span>
<span id="L127" rel="#L127">127</span>
<span id="L128" rel="#L128">128</span>
<span id="L129" rel="#L129">129</span>
<span id="L130" rel="#L130">130</span>
<span id="L131" rel="#L131">131</span>
<span id="L132" rel="#L132">132</span>
<span id="L133" rel="#L133">133</span>
<span id="L134" rel="#L134">134</span>
<span id="L135" rel="#L135">135</span>
<span id="L136" rel="#L136">136</span>
<span id="L137" rel="#L137">137</span>
<span id="L138" rel="#L138">138</span>
<span id="L139" rel="#L139">139</span>
<span id="L140" rel="#L140">140</span>
<span id="L141" rel="#L141">141</span>
<span id="L142" rel="#L142">142</span>
<span id="L143" rel="#L143">143</span>
<span id="L144" rel="#L144">144</span>
<span id="L145" rel="#L145">145</span>
<span id="L146" rel="#L146">146</span>
<span id="L147" rel="#L147">147</span>
<span id="L148" rel="#L148">148</span>
<span id="L149" rel="#L149">149</span>
<span id="L150" rel="#L150">150</span>
<span id="L151" rel="#L151">151</span>
<span id="L152" rel="#L152">152</span>
<span id="L153" rel="#L153">153</span>
<span id="L154" rel="#L154">154</span>
<span id="L155" rel="#L155">155</span>
<span id="L156" rel="#L156">156</span>
<span id="L157" rel="#L157">157</span>
<span id="L158" rel="#L158">158</span>
<span id="L159" rel="#L159">159</span>
<span id="L160" rel="#L160">160</span>
<span id="L161" rel="#L161">161</span>
<span id="L162" rel="#L162">162</span>
<span id="L163" rel="#L163">163</span>
<span id="L164" rel="#L164">164</span>
<span id="L165" rel="#L165">165</span>
<span id="L166" rel="#L166">166</span>
<span id="L167" rel="#L167">167</span>
<span id="L168" rel="#L168">168</span>
<span id="L169" rel="#L169">169</span>
<span id="L170" rel="#L170">170</span>
<span id="L171" rel="#L171">171</span>
<span id="L172" rel="#L172">172</span>
<span id="L173" rel="#L173">173</span>
<span id="L174" rel="#L174">174</span>
<span id="L175" rel="#L175">175</span>
<span id="L176" rel="#L176">176</span>
<span id="L177" rel="#L177">177</span>
<span id="L178" rel="#L178">178</span>
<span id="L179" rel="#L179">179</span>
<span id="L180" rel="#L180">180</span>
<span id="L181" rel="#L181">181</span>
<span id="L182" rel="#L182">182</span>
<span id="L183" rel="#L183">183</span>
<span id="L184" rel="#L184">184</span>
<span id="L185" rel="#L185">185</span>
<span id="L186" rel="#L186">186</span>
<span id="L187" rel="#L187">187</span>
<span id="L188" rel="#L188">188</span>
<span id="L189" rel="#L189">189</span>
<span id="L190" rel="#L190">190</span>
<span id="L191" rel="#L191">191</span>
<span id="L192" rel="#L192">192</span>
<span id="L193" rel="#L193">193</span>
<span id="L194" rel="#L194">194</span>
<span id="L195" rel="#L195">195</span>
<span id="L196" rel="#L196">196</span>
<span id="L197" rel="#L197">197</span>
<span id="L198" rel="#L198">198</span>
<span id="L199" rel="#L199">199</span>
<span id="L200" rel="#L200">200</span>
<span id="L201" rel="#L201">201</span>
<span id="L202" rel="#L202">202</span>
<span id="L203" rel="#L203">203</span>
<span id="L204" rel="#L204">204</span>
<span id="L205" rel="#L205">205</span>
<span id="L206" rel="#L206">206</span>
<span id="L207" rel="#L207">207</span>
<span id="L208" rel="#L208">208</span>
<span id="L209" rel="#L209">209</span>
<span id="L210" rel="#L210">210</span>
<span id="L211" rel="#L211">211</span>
<span id="L212" rel="#L212">212</span>
<span id="L213" rel="#L213">213</span>
<span id="L214" rel="#L214">214</span>
<span id="L215" rel="#L215">215</span>
<span id="L216" rel="#L216">216</span>
<span id="L217" rel="#L217">217</span>
<span id="L218" rel="#L218">218</span>
<span id="L219" rel="#L219">219</span>
<span id="L220" rel="#L220">220</span>
<span id="L221" rel="#L221">221</span>
<span id="L222" rel="#L222">222</span>
<span id="L223" rel="#L223">223</span>
<span id="L224" rel="#L224">224</span>
<span id="L225" rel="#L225">225</span>
<span id="L226" rel="#L226">226</span>
<span id="L227" rel="#L227">227</span>
<span id="L228" rel="#L228">228</span>
<span id="L229" rel="#L229">229</span>
<span id="L230" rel="#L230">230</span>
<span id="L231" rel="#L231">231</span>
<span id="L232" rel="#L232">232</span>
<span id="L233" rel="#L233">233</span>
<span id="L234" rel="#L234">234</span>
<span id="L235" rel="#L235">235</span>
<span id="L236" rel="#L236">236</span>
<span id="L237" rel="#L237">237</span>
<span id="L238" rel="#L238">238</span>
<span id="L239" rel="#L239">239</span>
<span id="L240" rel="#L240">240</span>
<span id="L241" rel="#L241">241</span>
<span id="L242" rel="#L242">242</span>
<span id="L243" rel="#L243">243</span>
<span id="L244" rel="#L244">244</span>
<span id="L245" rel="#L245">245</span>
<span id="L246" rel="#L246">246</span>
<span id="L247" rel="#L247">247</span>
<span id="L248" rel="#L248">248</span>
<span id="L249" rel="#L249">249</span>
<span id="L250" rel="#L250">250</span>
<span id="L251" rel="#L251">251</span>
<span id="L252" rel="#L252">252</span>
<span id="L253" rel="#L253">253</span>
<span id="L254" rel="#L254">254</span>
<span id="L255" rel="#L255">255</span>
<span id="L256" rel="#L256">256</span>
<span id="L257" rel="#L257">257</span>
<span id="L258" rel="#L258">258</span>
<span id="L259" rel="#L259">259</span>
<span id="L260" rel="#L260">260</span>
<span id="L261" rel="#L261">261</span>
<span id="L262" rel="#L262">262</span>
<span id="L263" rel="#L263">263</span>
<span id="L264" rel="#L264">264</span>
<span id="L265" rel="#L265">265</span>
<span id="L266" rel="#L266">266</span>
<span id="L267" rel="#L267">267</span>
<span id="L268" rel="#L268">268</span>
<span id="L269" rel="#L269">269</span>
<span id="L270" rel="#L270">270</span>
<span id="L271" rel="#L271">271</span>
<span id="L272" rel="#L272">272</span>
<span id="L273" rel="#L273">273</span>
<span id="L274" rel="#L274">274</span>
<span id="L275" rel="#L275">275</span>
<span id="L276" rel="#L276">276</span>
<span id="L277" rel="#L277">277</span>
<span id="L278" rel="#L278">278</span>
<span id="L279" rel="#L279">279</span>
<span id="L280" rel="#L280">280</span>
<span id="L281" rel="#L281">281</span>
<span id="L282" rel="#L282">282</span>
<span id="L283" rel="#L283">283</span>
<span id="L284" rel="#L284">284</span>
<span id="L285" rel="#L285">285</span>
<span id="L286" rel="#L286">286</span>
<span id="L287" rel="#L287">287</span>
<span id="L288" rel="#L288">288</span>
<span id="L289" rel="#L289">289</span>
<span id="L290" rel="#L290">290</span>
<span id="L291" rel="#L291">291</span>
<span id="L292" rel="#L292">292</span>
<span id="L293" rel="#L293">293</span>
<span id="L294" rel="#L294">294</span>
<span id="L295" rel="#L295">295</span>
<span id="L296" rel="#L296">296</span>
<span id="L297" rel="#L297">297</span>
<span id="L298" rel="#L298">298</span>
<span id="L299" rel="#L299">299</span>
<span id="L300" rel="#L300">300</span>
<span id="L301" rel="#L301">301</span>
<span id="L302" rel="#L302">302</span>
<span id="L303" rel="#L303">303</span>
<span id="L304" rel="#L304">304</span>
<span id="L305" rel="#L305">305</span>
<span id="L306" rel="#L306">306</span>
<span id="L307" rel="#L307">307</span>
<span id="L308" rel="#L308">308</span>
<span id="L309" rel="#L309">309</span>
<span id="L310" rel="#L310">310</span>
<span id="L311" rel="#L311">311</span>
<span id="L312" rel="#L312">312</span>
<span id="L313" rel="#L313">313</span>
<span id="L314" rel="#L314">314</span>
<span id="L315" rel="#L315">315</span>
<span id="L316" rel="#L316">316</span>
<span id="L317" rel="#L317">317</span>
<span id="L318" rel="#L318">318</span>
<span id="L319" rel="#L319">319</span>
<span id="L320" rel="#L320">320</span>
<span id="L321" rel="#L321">321</span>
<span id="L322" rel="#L322">322</span>
<span id="L323" rel="#L323">323</span>
<span id="L324" rel="#L324">324</span>
<span id="L325" rel="#L325">325</span>
<span id="L326" rel="#L326">326</span>
<span id="L327" rel="#L327">327</span>
<span id="L328" rel="#L328">328</span>
<span id="L329" rel="#L329">329</span>
<span id="L330" rel="#L330">330</span>
<span id="L331" rel="#L331">331</span>
<span id="L332" rel="#L332">332</span>
<span id="L333" rel="#L333">333</span>
<span id="L334" rel="#L334">334</span>
<span id="L335" rel="#L335">335</span>
<span id="L336" rel="#L336">336</span>
<span id="L337" rel="#L337">337</span>
<span id="L338" rel="#L338">338</span>
<span id="L339" rel="#L339">339</span>
<span id="L340" rel="#L340">340</span>
<span id="L341" rel="#L341">341</span>
<span id="L342" rel="#L342">342</span>
<span id="L343" rel="#L343">343</span>
<span id="L344" rel="#L344">344</span>
<span id="L345" rel="#L345">345</span>
<span id="L346" rel="#L346">346</span>
<span id="L347" rel="#L347">347</span>
<span id="L348" rel="#L348">348</span>
<span id="L349" rel="#L349">349</span>
<span id="L350" rel="#L350">350</span>
<span id="L351" rel="#L351">351</span>
<span id="L352" rel="#L352">352</span>
<span id="L353" rel="#L353">353</span>
<span id="L354" rel="#L354">354</span>
<span id="L355" rel="#L355">355</span>
<span id="L356" rel="#L356">356</span>
<span id="L357" rel="#L357">357</span>
<span id="L358" rel="#L358">358</span>
<span id="L359" rel="#L359">359</span>
<span id="L360" rel="#L360">360</span>
<span id="L361" rel="#L361">361</span>
<span id="L362" rel="#L362">362</span>
<span id="L363" rel="#L363">363</span>
<span id="L364" rel="#L364">364</span>
<span id="L365" rel="#L365">365</span>
<span id="L366" rel="#L366">366</span>
<span id="L367" rel="#L367">367</span>
<span id="L368" rel="#L368">368</span>
<span id="L369" rel="#L369">369</span>
<span id="L370" rel="#L370">370</span>
<span id="L371" rel="#L371">371</span>
<span id="L372" rel="#L372">372</span>
<span id="L373" rel="#L373">373</span>
<span id="L374" rel="#L374">374</span>
<span id="L375" rel="#L375">375</span>
<span id="L376" rel="#L376">376</span>
<span id="L377" rel="#L377">377</span>
<span id="L378" rel="#L378">378</span>
<span id="L379" rel="#L379">379</span>
<span id="L380" rel="#L380">380</span>
<span id="L381" rel="#L381">381</span>
<span id="L382" rel="#L382">382</span>
<span id="L383" rel="#L383">383</span>
<span id="L384" rel="#L384">384</span>
<span id="L385" rel="#L385">385</span>
<span id="L386" rel="#L386">386</span>
<span id="L387" rel="#L387">387</span>
<span id="L388" rel="#L388">388</span>
<span id="L389" rel="#L389">389</span>
<span id="L390" rel="#L390">390</span>
<span id="L391" rel="#L391">391</span>
<span id="L392" rel="#L392">392</span>
<span id="L393" rel="#L393">393</span>
<span id="L394" rel="#L394">394</span>
<span id="L395" rel="#L395">395</span>
<span id="L396" rel="#L396">396</span>
<span id="L397" rel="#L397">397</span>
<span id="L398" rel="#L398">398</span>
<span id="L399" rel="#L399">399</span>
<span id="L400" rel="#L400">400</span>
<span id="L401" rel="#L401">401</span>
<span id="L402" rel="#L402">402</span>
<span id="L403" rel="#L403">403</span>
<span id="L404" rel="#L404">404</span>
<span id="L405" rel="#L405">405</span>
<span id="L406" rel="#L406">406</span>
<span id="L407" rel="#L407">407</span>
<span id="L408" rel="#L408">408</span>
<span id="L409" rel="#L409">409</span>
<span id="L410" rel="#L410">410</span>
<span id="L411" rel="#L411">411</span>
<span id="L412" rel="#L412">412</span>
<span id="L413" rel="#L413">413</span>
<span id="L414" rel="#L414">414</span>
<span id="L415" rel="#L415">415</span>
<span id="L416" rel="#L416">416</span>
<span id="L417" rel="#L417">417</span>
<span id="L418" rel="#L418">418</span>
<span id="L419" rel="#L419">419</span>
<span id="L420" rel="#L420">420</span>
<span id="L421" rel="#L421">421</span>
<span id="L422" rel="#L422">422</span>
<span id="L423" rel="#L423">423</span>
<span id="L424" rel="#L424">424</span>
<span id="L425" rel="#L425">425</span>
<span id="L426" rel="#L426">426</span>
<span id="L427" rel="#L427">427</span>
<span id="L428" rel="#L428">428</span>
<span id="L429" rel="#L429">429</span>
<span id="L430" rel="#L430">430</span>
<span id="L431" rel="#L431">431</span>
<span id="L432" rel="#L432">432</span>
<span id="L433" rel="#L433">433</span>
<span id="L434" rel="#L434">434</span>
<span id="L435" rel="#L435">435</span>
<span id="L436" rel="#L436">436</span>
<span id="L437" rel="#L437">437</span>
<span id="L438" rel="#L438">438</span>
<span id="L439" rel="#L439">439</span>
<span id="L440" rel="#L440">440</span>
<span id="L441" rel="#L441">441</span>
<span id="L442" rel="#L442">442</span>
<span id="L443" rel="#L443">443</span>
<span id="L444" rel="#L444">444</span>
<span id="L445" rel="#L445">445</span>
<span id="L446" rel="#L446">446</span>
<span id="L447" rel="#L447">447</span>
<span id="L448" rel="#L448">448</span>
<span id="L449" rel="#L449">449</span>
<span id="L450" rel="#L450">450</span>
<span id="L451" rel="#L451">451</span>
<span id="L452" rel="#L452">452</span>
<span id="L453" rel="#L453">453</span>
<span id="L454" rel="#L454">454</span>
<span id="L455" rel="#L455">455</span>
<span id="L456" rel="#L456">456</span>
<span id="L457" rel="#L457">457</span>
<span id="L458" rel="#L458">458</span>
<span id="L459" rel="#L459">459</span>
<span id="L460" rel="#L460">460</span>
<span id="L461" rel="#L461">461</span>
<span id="L462" rel="#L462">462</span>
<span id="L463" rel="#L463">463</span>
<span id="L464" rel="#L464">464</span>
<span id="L465" rel="#L465">465</span>
<span id="L466" rel="#L466">466</span>
<span id="L467" rel="#L467">467</span>
<span id="L468" rel="#L468">468</span>
<span id="L469" rel="#L469">469</span>
<span id="L470" rel="#L470">470</span>
<span id="L471" rel="#L471">471</span>
<span id="L472" rel="#L472">472</span>
<span id="L473" rel="#L473">473</span>
<span id="L474" rel="#L474">474</span>
<span id="L475" rel="#L475">475</span>
<span id="L476" rel="#L476">476</span>
<span id="L477" rel="#L477">477</span>
<span id="L478" rel="#L478">478</span>
<span id="L479" rel="#L479">479</span>
<span id="L480" rel="#L480">480</span>
<span id="L481" rel="#L481">481</span>
<span id="L482" rel="#L482">482</span>
<span id="L483" rel="#L483">483</span>
<span id="L484" rel="#L484">484</span>
<span id="L485" rel="#L485">485</span>
<span id="L486" rel="#L486">486</span>
<span id="L487" rel="#L487">487</span>
<span id="L488" rel="#L488">488</span>
<span id="L489" rel="#L489">489</span>
<span id="L490" rel="#L490">490</span>
<span id="L491" rel="#L491">491</span>
<span id="L492" rel="#L492">492</span>
<span id="L493" rel="#L493">493</span>
<span id="L494" rel="#L494">494</span>
<span id="L495" rel="#L495">495</span>
<span id="L496" rel="#L496">496</span>
<span id="L497" rel="#L497">497</span>
<span id="L498" rel="#L498">498</span>
<span id="L499" rel="#L499">499</span>
<span id="L500" rel="#L500">500</span>
<span id="L501" rel="#L501">501</span>
<span id="L502" rel="#L502">502</span>
<span id="L503" rel="#L503">503</span>
<span id="L504" rel="#L504">504</span>
<span id="L505" rel="#L505">505</span>
<span id="L506" rel="#L506">506</span>
<span id="L507" rel="#L507">507</span>
<span id="L508" rel="#L508">508</span>
<span id="L509" rel="#L509">509</span>
<span id="L510" rel="#L510">510</span>
<span id="L511" rel="#L511">511</span>
<span id="L512" rel="#L512">512</span>
<span id="L513" rel="#L513">513</span>
<span id="L514" rel="#L514">514</span>
<span id="L515" rel="#L515">515</span>
<span id="L516" rel="#L516">516</span>
<span id="L517" rel="#L517">517</span>
<span id="L518" rel="#L518">518</span>
<span id="L519" rel="#L519">519</span>
<span id="L520" rel="#L520">520</span>
<span id="L521" rel="#L521">521</span>
<span id="L522" rel="#L522">522</span>
<span id="L523" rel="#L523">523</span>
<span id="L524" rel="#L524">524</span>
<span id="L525" rel="#L525">525</span>
<span id="L526" rel="#L526">526</span>
<span id="L527" rel="#L527">527</span>
<span id="L528" rel="#L528">528</span>
<span id="L529" rel="#L529">529</span>
<span id="L530" rel="#L530">530</span>
<span id="L531" rel="#L531">531</span>
<span id="L532" rel="#L532">532</span>
<span id="L533" rel="#L533">533</span>
<span id="L534" rel="#L534">534</span>
<span id="L535" rel="#L535">535</span>
<span id="L536" rel="#L536">536</span>
<span id="L537" rel="#L537">537</span>
<span id="L538" rel="#L538">538</span>
<span id="L539" rel="#L539">539</span>
<span id="L540" rel="#L540">540</span>
<span id="L541" rel="#L541">541</span>
<span id="L542" rel="#L542">542</span>
<span id="L543" rel="#L543">543</span>
<span id="L544" rel="#L544">544</span>
<span id="L545" rel="#L545">545</span>
<span id="L546" rel="#L546">546</span>
<span id="L547" rel="#L547">547</span>
<span id="L548" rel="#L548">548</span>
<span id="L549" rel="#L549">549</span>
<span id="L550" rel="#L550">550</span>
<span id="L551" rel="#L551">551</span>
<span id="L552" rel="#L552">552</span>
<span id="L553" rel="#L553">553</span>
<span id="L554" rel="#L554">554</span>
<span id="L555" rel="#L555">555</span>
<span id="L556" rel="#L556">556</span>
<span id="L557" rel="#L557">557</span>
<span id="L558" rel="#L558">558</span>
<span id="L559" rel="#L559">559</span>
<span id="L560" rel="#L560">560</span>
<span id="L561" rel="#L561">561</span>
<span id="L562" rel="#L562">562</span>
<span id="L563" rel="#L563">563</span>
<span id="L564" rel="#L564">564</span>
<span id="L565" rel="#L565">565</span>
<span id="L566" rel="#L566">566</span>
<span id="L567" rel="#L567">567</span>
<span id="L568" rel="#L568">568</span>
<span id="L569" rel="#L569">569</span>
<span id="L570" rel="#L570">570</span>
<span id="L571" rel="#L571">571</span>
<span id="L572" rel="#L572">572</span>
<span id="L573" rel="#L573">573</span>
<span id="L574" rel="#L574">574</span>
<span id="L575" rel="#L575">575</span>
<span id="L576" rel="#L576">576</span>
<span id="L577" rel="#L577">577</span>
<span id="L578" rel="#L578">578</span>
<span id="L579" rel="#L579">579</span>
<span id="L580" rel="#L580">580</span>
<span id="L581" rel="#L581">581</span>
<span id="L582" rel="#L582">582</span>
<span id="L583" rel="#L583">583</span>
<span id="L584" rel="#L584">584</span>
<span id="L585" rel="#L585">585</span>
<span id="L586" rel="#L586">586</span>
<span id="L587" rel="#L587">587</span>
<span id="L588" rel="#L588">588</span>
<span id="L589" rel="#L589">589</span>
<span id="L590" rel="#L590">590</span>
<span id="L591" rel="#L591">591</span>
<span id="L592" rel="#L592">592</span>
<span id="L593" rel="#L593">593</span>
<span id="L594" rel="#L594">594</span>
<span id="L595" rel="#L595">595</span>
<span id="L596" rel="#L596">596</span>
<span id="L597" rel="#L597">597</span>
<span id="L598" rel="#L598">598</span>
<span id="L599" rel="#L599">599</span>
<span id="L600" rel="#L600">600</span>
<span id="L601" rel="#L601">601</span>
<span id="L602" rel="#L602">602</span>
<span id="L603" rel="#L603">603</span>
<span id="L604" rel="#L604">604</span>
<span id="L605" rel="#L605">605</span>
<span id="L606" rel="#L606">606</span>
<span id="L607" rel="#L607">607</span>
<span id="L608" rel="#L608">608</span>
<span id="L609" rel="#L609">609</span>
<span id="L610" rel="#L610">610</span>
<span id="L611" rel="#L611">611</span>
<span id="L612" rel="#L612">612</span>
<span id="L613" rel="#L613">613</span>
<span id="L614" rel="#L614">614</span>
<span id="L615" rel="#L615">615</span>
<span id="L616" rel="#L616">616</span>
<span id="L617" rel="#L617">617</span>
<span id="L618" rel="#L618">618</span>
<span id="L619" rel="#L619">619</span>
<span id="L620" rel="#L620">620</span>
<span id="L621" rel="#L621">621</span>
<span id="L622" rel="#L622">622</span>
<span id="L623" rel="#L623">623</span>
<span id="L624" rel="#L624">624</span>
<span id="L625" rel="#L625">625</span>
<span id="L626" rel="#L626">626</span>
<span id="L627" rel="#L627">627</span>
<span id="L628" rel="#L628">628</span>
<span id="L629" rel="#L629">629</span>
<span id="L630" rel="#L630">630</span>
<span id="L631" rel="#L631">631</span>
<span id="L632" rel="#L632">632</span>
<span id="L633" rel="#L633">633</span>
<span id="L634" rel="#L634">634</span>
<span id="L635" rel="#L635">635</span>
<span id="L636" rel="#L636">636</span>
<span id="L637" rel="#L637">637</span>
<span id="L638" rel="#L638">638</span>
<span id="L639" rel="#L639">639</span>
<span id="L640" rel="#L640">640</span>
<span id="L641" rel="#L641">641</span>
<span id="L642" rel="#L642">642</span>
<span id="L643" rel="#L643">643</span>
<span id="L644" rel="#L644">644</span>
<span id="L645" rel="#L645">645</span>
<span id="L646" rel="#L646">646</span>
<span id="L647" rel="#L647">647</span>
<span id="L648" rel="#L648">648</span>
<span id="L649" rel="#L649">649</span>
<span id="L650" rel="#L650">650</span>
<span id="L651" rel="#L651">651</span>
<span id="L652" rel="#L652">652</span>
<span id="L653" rel="#L653">653</span>
</pre>
          </td>
          <td width="100%">
                <div class="highlight"><pre><div class='line' id='LC1'><span class="cm">/************************</span></div><div class='line' id='LC2'><span class="cm">jquery-timepicker</span></div><div class='line' id='LC3'><span class="cm">http://jonthornton.github.com/jquery-timepicker/</span></div><div class='line' id='LC4'><br/></div><div class='line' id='LC5'><span class="cm">requires jQuery 1.7+</span></div><div class='line' id='LC6'><span class="cm">************************/</span></div><div class='line' id='LC7'><br/></div><div class='line' id='LC8'><br/></div><div class='line' id='LC9'><span class="p">(</span><span class="kd">function</span> <span class="p">(</span><span class="nx">factory</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC10'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> <span class="p">(</span><span class="k">typeof</span> <span class="nx">define</span> <span class="o">===</span> <span class="s1">&#39;function&#39;</span> <span class="o">&amp;&amp;</span> <span class="nx">define</span><span class="p">.</span><span class="nx">amd</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC11'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c1">// AMD. Register as an anonymous module.</span></div><div class='line' id='LC12'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="nx">define</span><span class="p">([</span><span class="s1">&#39;jquery&#39;</span><span class="p">],</span> <span class="nx">factory</span><span class="p">);</span></div><div class='line' id='LC13'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="p">}</span> <span class="k">else</span> <span class="p">{</span></div><div class='line' id='LC14'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="c1">// Browser globals</span></div><div class='line' id='LC15'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="nx">factory</span><span class="p">(</span><span class="nx">jQuery</span><span class="p">);</span></div><div class='line' id='LC16'>&nbsp;&nbsp;&nbsp;&nbsp;<span class="p">}</span></div><div class='line' id='LC17'><span class="p">}(</span><span class="kd">function</span> <span class="p">(</span><span class="nx">$</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC18'>	<span class="kd">var</span> <span class="nx">_baseDate</span> <span class="o">=</span> <span class="nx">_generateBaseDate</span><span class="p">();</span></div><div class='line' id='LC19'>	<span class="kd">var</span> <span class="nx">_ONE_DAY</span> <span class="o">=</span> <span class="mi">86400</span><span class="p">;</span></div><div class='line' id='LC20'>	<span class="kd">var</span> <span class="nx">_closeEvent</span> <span class="o">=</span> <span class="s1">&#39;ontouchstart&#39;</span> <span class="k">in</span> <span class="nb">document</span> <span class="o">?</span> <span class="s1">&#39;touchstart&#39;</span> <span class="o">:</span> <span class="s1">&#39;mousedown&#39;</span><span class="p">;</span></div><div class='line' id='LC21'>	<span class="kd">var</span> <span class="nx">_defaults</span> <span class="o">=</span>	<span class="p">{</span></div><div class='line' id='LC22'>		<span class="nx">className</span><span class="o">:</span> <span class="kc">null</span><span class="p">,</span></div><div class='line' id='LC23'>		<span class="nx">minTime</span><span class="o">:</span> <span class="kc">null</span><span class="p">,</span></div><div class='line' id='LC24'>		<span class="nx">maxTime</span><span class="o">:</span> <span class="kc">null</span><span class="p">,</span></div><div class='line' id='LC25'>		<span class="nx">durationTime</span><span class="o">:</span> <span class="kc">null</span><span class="p">,</span></div><div class='line' id='LC26'>		<span class="nx">step</span><span class="o">:</span> <span class="mi">30</span><span class="p">,</span></div><div class='line' id='LC27'>		<span class="nx">showDuration</span><span class="o">:</span> <span class="kc">false</span><span class="p">,</span></div><div class='line' id='LC28'>		<span class="nx">timeFormat</span><span class="o">:</span> <span class="s1">&#39;g:ia&#39;</span><span class="p">,</span></div><div class='line' id='LC29'>		<span class="nx">scrollDefaultNow</span><span class="o">:</span> <span class="kc">false</span><span class="p">,</span></div><div class='line' id='LC30'>		<span class="nx">scrollDefaultTime</span><span class="o">:</span> <span class="kc">false</span><span class="p">,</span></div><div class='line' id='LC31'>		<span class="nx">selectOnBlur</span><span class="o">:</span> <span class="kc">false</span><span class="p">,</span></div><div class='line' id='LC32'>		<span class="nx">appendTo</span><span class="o">:</span> <span class="s1">&#39;body&#39;</span></div><div class='line' id='LC33'>	<span class="p">};</span></div><div class='line' id='LC34'>	<span class="kd">var</span> <span class="nx">_lang</span> <span class="o">=</span> <span class="p">{</span></div><div class='line' id='LC35'>		<span class="nx">decimal</span><span class="o">:</span> <span class="s1">&#39;.&#39;</span><span class="p">,</span></div><div class='line' id='LC36'>		<span class="nx">mins</span><span class="o">:</span> <span class="s1">&#39;mins&#39;</span><span class="p">,</span></div><div class='line' id='LC37'>		<span class="nx">hr</span><span class="o">:</span> <span class="s1">&#39;hr&#39;</span><span class="p">,</span></div><div class='line' id='LC38'>		<span class="nx">hrs</span><span class="o">:</span> <span class="s1">&#39;hrs&#39;</span></div><div class='line' id='LC39'>	<span class="p">};</span></div><div class='line' id='LC40'>	<span class="kd">var</span> <span class="nx">globalInit</span> <span class="o">=</span> <span class="kc">false</span><span class="p">;</span></div><div class='line' id='LC41'><br/></div><div class='line' id='LC42'>	<span class="kd">var</span> <span class="nx">methods</span> <span class="o">=</span></div><div class='line' id='LC43'>	<span class="p">{</span></div><div class='line' id='LC44'>		<span class="nx">init</span><span class="o">:</span> <span class="kd">function</span><span class="p">(</span><span class="nx">options</span><span class="p">)</span></div><div class='line' id='LC45'>		<span class="p">{</span></div><div class='line' id='LC46'>			<span class="k">return</span> <span class="k">this</span><span class="p">.</span><span class="nx">each</span><span class="p">(</span><span class="kd">function</span><span class="p">()</span></div><div class='line' id='LC47'>			<span class="p">{</span></div><div class='line' id='LC48'>				<span class="kd">var</span> <span class="nx">self</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="k">this</span><span class="p">);</span></div><div class='line' id='LC49'><br/></div><div class='line' id='LC50'>				<span class="c1">// convert dropdowns to text input</span></div><div class='line' id='LC51'>				<span class="k">if</span> <span class="p">(</span><span class="nx">self</span><span class="p">[</span><span class="mi">0</span><span class="p">].</span><span class="nx">tagName</span> <span class="o">==</span> <span class="s1">&#39;SELECT&#39;</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC52'>					<span class="kd">var</span> <span class="nx">input</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="s1">&#39;&lt;input /&gt;&#39;</span><span class="p">);</span></div><div class='line' id='LC53'>					<span class="kd">var</span> <span class="nx">attrs</span> <span class="o">=</span> <span class="p">{</span> <span class="s1">&#39;type&#39;</span><span class="o">:</span> <span class="s1">&#39;text&#39;</span><span class="p">,</span> <span class="s1">&#39;value&#39;</span><span class="o">:</span> <span class="nx">self</span><span class="p">.</span><span class="nx">val</span><span class="p">()</span> <span class="p">};</span></div><div class='line' id='LC54'>					<span class="kd">var</span> <span class="nx">raw_attrs</span> <span class="o">=</span> <span class="nx">self</span><span class="p">[</span><span class="mi">0</span><span class="p">].</span><span class="nx">attributes</span><span class="p">;</span></div><div class='line' id='LC55'><br/></div><div class='line' id='LC56'>					<span class="k">for</span> <span class="p">(</span><span class="kd">var</span> <span class="nx">i</span><span class="o">=</span><span class="mi">0</span><span class="p">;</span> <span class="nx">i</span> <span class="o">&lt;</span> <span class="nx">raw_attrs</span><span class="p">.</span><span class="nx">length</span><span class="p">;</span> <span class="nx">i</span><span class="o">++</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC57'>						<span class="nx">attrs</span><span class="p">[</span><span class="nx">raw_attrs</span><span class="p">[</span><span class="nx">i</span><span class="p">].</span><span class="nx">nodeName</span><span class="p">]</span> <span class="o">=</span> <span class="nx">raw_attrs</span><span class="p">[</span><span class="nx">i</span><span class="p">].</span><span class="nx">nodeValue</span><span class="p">;</span></div><div class='line' id='LC58'>					<span class="p">}</span></div><div class='line' id='LC59'><br/></div><div class='line' id='LC60'>					<span class="nx">input</span><span class="p">.</span><span class="nx">attr</span><span class="p">(</span><span class="nx">attrs</span><span class="p">);</span></div><div class='line' id='LC61'>					<span class="nx">self</span><span class="p">.</span><span class="nx">replaceWith</span><span class="p">(</span><span class="nx">input</span><span class="p">);</span></div><div class='line' id='LC62'>					<span class="nx">self</span> <span class="o">=</span> <span class="nx">input</span><span class="p">;</span></div><div class='line' id='LC63'>				<span class="p">}</span></div><div class='line' id='LC64'><br/></div><div class='line' id='LC65'>				<span class="kd">var</span> <span class="nx">settings</span> <span class="o">=</span> <span class="nx">$</span><span class="p">.</span><span class="nx">extend</span><span class="p">({},</span> <span class="nx">_defaults</span><span class="p">);</span></div><div class='line' id='LC66'><br/></div><div class='line' id='LC67'>				<span class="k">if</span> <span class="p">(</span><span class="nx">options</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC68'>					<span class="nx">settings</span> <span class="o">=</span> <span class="nx">$</span><span class="p">.</span><span class="nx">extend</span><span class="p">(</span><span class="nx">settings</span><span class="p">,</span> <span class="nx">options</span><span class="p">);</span></div><div class='line' id='LC69'>				<span class="p">}</span></div><div class='line' id='LC70'><br/></div><div class='line' id='LC71'>				<span class="k">if</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">minTime</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC72'>					<span class="nx">settings</span><span class="p">.</span><span class="nx">minTime</span> <span class="o">=</span> <span class="nx">_time2int</span><span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">minTime</span><span class="p">);</span></div><div class='line' id='LC73'>				<span class="p">}</span></div><div class='line' id='LC74'><br/></div><div class='line' id='LC75'>				<span class="k">if</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">maxTime</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC76'>					<span class="nx">settings</span><span class="p">.</span><span class="nx">maxTime</span> <span class="o">=</span> <span class="nx">_time2int</span><span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">maxTime</span><span class="p">);</span></div><div class='line' id='LC77'>				<span class="p">}</span></div><div class='line' id='LC78'><br/></div><div class='line' id='LC79'>				<span class="k">if</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">durationTime</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC80'>					<span class="nx">settings</span><span class="p">.</span><span class="nx">durationTime</span> <span class="o">=</span> <span class="nx">_time2int</span><span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">durationTime</span><span class="p">);</span></div><div class='line' id='LC81'>				<span class="p">}</span></div><div class='line' id='LC82'><br/></div><div class='line' id='LC83'>				<span class="k">if</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">lang</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC84'>					<span class="nx">_lang</span> <span class="o">=</span> <span class="nx">$</span><span class="p">.</span><span class="nx">extend</span><span class="p">(</span><span class="nx">_lang</span><span class="p">,</span> <span class="nx">settings</span><span class="p">.</span><span class="nx">lang</span><span class="p">);</span></div><div class='line' id='LC85'>				<span class="p">}</span></div><div class='line' id='LC86'><br/></div><div class='line' id='LC87'>				<span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-settings&#39;</span><span class="p">,</span> <span class="nx">settings</span><span class="p">);</span></div><div class='line' id='LC88'>				<span class="nx">self</span><span class="p">.</span><span class="nx">attr</span><span class="p">(</span><span class="s1">&#39;autocomplete&#39;</span><span class="p">,</span> <span class="s1">&#39;off&#39;</span><span class="p">);</span></div><div class='line' id='LC89'>				<span class="nx">self</span><span class="p">.</span><span class="nx">on</span><span class="p">(</span><span class="s1">&#39;click.timepicker focus.timepicker&#39;</span><span class="p">,</span> <span class="nx">methods</span><span class="p">.</span><span class="nx">show</span><span class="p">);</span></div><div class='line' id='LC90'>				<span class="nx">self</span><span class="p">.</span><span class="nx">on</span><span class="p">(</span><span class="s1">&#39;blur.timepicker&#39;</span><span class="p">,</span> <span class="nx">_formatValue</span><span class="p">);</span></div><div class='line' id='LC91'>				<span class="nx">self</span><span class="p">.</span><span class="nx">on</span><span class="p">(</span><span class="s1">&#39;keydown.timepicker&#39;</span><span class="p">,</span> <span class="nx">_keyhandler</span><span class="p">);</span></div><div class='line' id='LC92'>				<span class="nx">self</span><span class="p">.</span><span class="nx">addClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-input&#39;</span><span class="p">);</span></div><div class='line' id='LC93'><br/></div><div class='line' id='LC94'>				<span class="nx">_formatValue</span><span class="p">.</span><span class="nx">call</span><span class="p">(</span><span class="nx">self</span><span class="p">.</span><span class="nx">get</span><span class="p">(</span><span class="mi">0</span><span class="p">));</span></div><div class='line' id='LC95'><br/></div><div class='line' id='LC96'>				<span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nx">globalInit</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC97'>					<span class="c1">// close the dropdown when container loses focus</span></div><div class='line' id='LC98'>					<span class="nx">$</span><span class="p">(</span><span class="s1">&#39;body&#39;</span><span class="p">).</span><span class="nx">on</span><span class="p">(</span><span class="nx">_closeEvent</span><span class="p">,</span> <span class="kd">function</span><span class="p">(</span><span class="nx">e</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC99'>						<span class="kd">var</span> <span class="nx">target</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="nx">e</span><span class="p">.</span><span class="nx">target</span><span class="p">);</span></div><div class='line' id='LC100'>						<span class="kd">var</span> <span class="nx">input</span> <span class="o">=</span> <span class="nx">target</span><span class="p">.</span><span class="nx">closest</span><span class="p">(</span><span class="s1">&#39;.ui-timepicker-input&#39;</span><span class="p">);</span></div><div class='line' id='LC101'>						<span class="k">if</span> <span class="p">(</span><span class="nx">input</span><span class="p">.</span><span class="nx">length</span> <span class="o">===</span> <span class="mi">0</span> <span class="o">&amp;&amp;</span> <span class="nx">target</span><span class="p">.</span><span class="nx">closest</span><span class="p">(</span><span class="s1">&#39;.ui-timepicker-list&#39;</span><span class="p">).</span><span class="nx">length</span> <span class="o">===</span> <span class="mi">0</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC102'>							<span class="nx">methods</span><span class="p">.</span><span class="nx">hide</span><span class="p">();</span></div><div class='line' id='LC103'>							<span class="c1">// needs to blur the active element to remove keyboard on touch devices</span></div><div class='line' id='LC104'>							<span class="nb">document</span><span class="p">.</span><span class="nx">activeElement</span><span class="p">.</span><span class="nx">blur</span><span class="p">();</span></div><div class='line' id='LC105'>						<span class="p">}</span></div><div class='line' id='LC106'>					<span class="p">});</span></div><div class='line' id='LC107'>					<span class="nx">globalInit</span> <span class="o">=</span> <span class="kc">true</span><span class="p">;</span></div><div class='line' id='LC108'>				<span class="p">}</span></div><div class='line' id='LC109'>			<span class="p">});</span></div><div class='line' id='LC110'>		<span class="p">},</span></div><div class='line' id='LC111'><br/></div><div class='line' id='LC112'>		<span class="nx">show</span><span class="o">:</span> <span class="kd">function</span><span class="p">(</span><span class="nx">e</span><span class="p">)</span></div><div class='line' id='LC113'>		<span class="p">{</span></div><div class='line' id='LC114'>			<span class="kd">var</span> <span class="nx">self</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="k">this</span><span class="p">);</span></div><div class='line' id='LC115'>			<span class="kd">var</span> <span class="nx">list</span> <span class="o">=</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-list&#39;</span><span class="p">);</span></div><div class='line' id='LC116'><br/></div><div class='line' id='LC117'>			<span class="c1">// check if input is readonly</span></div><div class='line' id='LC118'>			<span class="k">if</span> <span class="p">(</span><span class="nx">self</span><span class="p">.</span><span class="nx">attr</span><span class="p">(</span><span class="s1">&#39;readonly&#39;</span><span class="p">))</span> <span class="p">{</span></div><div class='line' id='LC119'>				<span class="k">return</span><span class="p">;</span></div><div class='line' id='LC120'>			<span class="p">}</span></div><div class='line' id='LC121'><br/></div><div class='line' id='LC122'>			<span class="c1">// check if list needs to be rendered</span></div><div class='line' id='LC123'>			<span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nx">list</span> <span class="o">||</span> <span class="nx">list</span><span class="p">.</span><span class="nx">length</span> <span class="o">===</span> <span class="mi">0</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC124'>				<span class="nx">_render</span><span class="p">(</span><span class="nx">self</span><span class="p">);</span></div><div class='line' id='LC125'>				<span class="nx">list</span> <span class="o">=</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-list&#39;</span><span class="p">);</span></div><div class='line' id='LC126'>			<span class="p">}</span></div><div class='line' id='LC127'><br/></div><div class='line' id='LC128'>			<span class="c1">// check if a flag was set to close this picker</span></div><div class='line' id='LC129'>			<span class="k">if</span> <span class="p">(</span><span class="nx">self</span><span class="p">.</span><span class="nx">hasClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-hideme&#39;</span><span class="p">))</span> <span class="p">{</span></div><div class='line' id='LC130'>				<span class="nx">self</span><span class="p">.</span><span class="nx">removeClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-hideme&#39;</span><span class="p">);</span></div><div class='line' id='LC131'>				<span class="nx">list</span><span class="p">.</span><span class="nx">hide</span><span class="p">();</span></div><div class='line' id='LC132'>				<span class="k">return</span><span class="p">;</span></div><div class='line' id='LC133'>			<span class="p">}</span></div><div class='line' id='LC134'><br/></div><div class='line' id='LC135'>			<span class="k">if</span> <span class="p">(</span><span class="nx">list</span><span class="p">.</span><span class="nx">is</span><span class="p">(</span><span class="s1">&#39;:visible&#39;</span><span class="p">))</span> <span class="p">{</span></div><div class='line' id='LC136'>				<span class="k">return</span><span class="p">;</span></div><div class='line' id='LC137'>			<span class="p">}</span></div><div class='line' id='LC138'><br/></div><div class='line' id='LC139'>			<span class="c1">// make sure other pickers are hidden</span></div><div class='line' id='LC140'>			<span class="nx">methods</span><span class="p">.</span><span class="nx">hide</span><span class="p">();</span></div><div class='line' id='LC141'><br/></div><div class='line' id='LC142'>			<span class="k">if</span> <span class="p">((</span><span class="nx">self</span><span class="p">.</span><span class="nx">offset</span><span class="p">().</span><span class="nx">top</span> <span class="o">+</span> <span class="nx">self</span><span class="p">.</span><span class="nx">outerHeight</span><span class="p">(</span><span class="kc">true</span><span class="p">)</span> <span class="o">+</span> <span class="nx">list</span><span class="p">.</span><span class="nx">outerHeight</span><span class="p">())</span> <span class="o">&gt;</span> <span class="nx">$</span><span class="p">(</span><span class="nb">window</span><span class="p">).</span><span class="nx">height</span><span class="p">()</span> <span class="o">+</span> <span class="nx">$</span><span class="p">(</span><span class="nb">window</span><span class="p">).</span><span class="nx">scrollTop</span><span class="p">())</span> <span class="p">{</span></div><div class='line' id='LC143'>				<span class="c1">// position the dropdown on top</span></div><div class='line' id='LC144'>				<span class="nx">list</span><span class="p">.</span><span class="nx">css</span><span class="p">({</span> <span class="s1">&#39;left&#39;</span><span class="o">:</span><span class="p">(</span><span class="nx">self</span><span class="p">.</span><span class="nx">offset</span><span class="p">().</span><span class="nx">left</span><span class="p">),</span> <span class="s1">&#39;top&#39;</span><span class="o">:</span> <span class="nx">self</span><span class="p">.</span><span class="nx">offset</span><span class="p">().</span><span class="nx">top</span> <span class="o">-</span> <span class="nx">list</span><span class="p">.</span><span class="nx">outerHeight</span><span class="p">()</span> <span class="p">});</span></div><div class='line' id='LC145'>			<span class="p">}</span> <span class="k">else</span> <span class="p">{</span></div><div class='line' id='LC146'>				<span class="c1">// put it under the input</span></div><div class='line' id='LC147'>				<span class="nx">list</span><span class="p">.</span><span class="nx">css</span><span class="p">({</span> <span class="s1">&#39;left&#39;</span><span class="o">:</span><span class="p">(</span><span class="nx">self</span><span class="p">.</span><span class="nx">offset</span><span class="p">().</span><span class="nx">left</span><span class="p">),</span> <span class="s1">&#39;top&#39;</span><span class="o">:</span> <span class="nx">self</span><span class="p">.</span><span class="nx">offset</span><span class="p">().</span><span class="nx">top</span> <span class="o">+</span> <span class="nx">self</span><span class="p">.</span><span class="nx">outerHeight</span><span class="p">()</span> <span class="p">});</span></div><div class='line' id='LC148'>			<span class="p">}</span></div><div class='line' id='LC149'><br/></div><div class='line' id='LC150'>			<span class="nx">list</span><span class="p">.</span><span class="nx">show</span><span class="p">();</span></div><div class='line' id='LC151'><br/></div><div class='line' id='LC152'>			<span class="kd">var</span> <span class="nx">settings</span> <span class="o">=</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-settings&#39;</span><span class="p">);</span></div><div class='line' id='LC153'>			<span class="c1">// position scrolling</span></div><div class='line' id='LC154'>			<span class="kd">var</span> <span class="nx">selected</span> <span class="o">=</span> <span class="nx">list</span><span class="p">.</span><span class="nx">find</span><span class="p">(</span><span class="s1">&#39;.ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC155'><br/></div><div class='line' id='LC156'>			<span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nx">selected</span><span class="p">.</span><span class="nx">length</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC157'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> <span class="p">(</span><span class="nx">self</span><span class="p">.</span><span class="nx">val</span><span class="p">())</span> <span class="p">{</span></div><div class='line' id='LC158'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="nx">selected</span> <span class="o">=</span> <span class="nx">_findRow</span><span class="p">(</span><span class="nx">self</span><span class="p">,</span> <span class="nx">list</span><span class="p">,</span> <span class="nx">_time2int</span><span class="p">(</span><span class="nx">self</span><span class="p">.</span><span class="nx">val</span><span class="p">()));</span></div><div class='line' id='LC159'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="p">}</span> <span class="k">else</span> <span class="k">if</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">scrollDefaultNow</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC160'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="nx">selected</span> <span class="o">=</span> <span class="nx">_findRow</span><span class="p">(</span><span class="nx">self</span><span class="p">,</span> <span class="nx">list</span><span class="p">,</span> <span class="nx">_time2int</span><span class="p">(</span><span class="k">new</span> <span class="nb">Date</span><span class="p">()));</span></div><div class='line' id='LC161'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="p">}</span> <span class="k">else</span> <span class="k">if</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">scrollDefaultTime</span> <span class="o">!==</span> <span class="kc">false</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC162'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="nx">selected</span> <span class="o">=</span> <span class="nx">_findRow</span><span class="p">(</span><span class="nx">self</span><span class="p">,</span> <span class="nx">list</span><span class="p">,</span> <span class="nx">_time2int</span><span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">scrollDefaultTime</span><span class="p">));</span></div><div class='line' id='LC163'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="p">}</span></div><div class='line' id='LC164'>			<span class="p">}</span></div><div class='line' id='LC165'><br/></div><div class='line' id='LC166'>			<span class="k">if</span> <span class="p">(</span><span class="nx">selected</span> <span class="o">&amp;&amp;</span> <span class="nx">selected</span><span class="p">.</span><span class="nx">length</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC167'>				<span class="kd">var</span> <span class="nx">topOffset</span> <span class="o">=</span> <span class="nx">list</span><span class="p">.</span><span class="nx">scrollTop</span><span class="p">()</span> <span class="o">+</span> <span class="nx">selected</span><span class="p">.</span><span class="nx">position</span><span class="p">().</span><span class="nx">top</span> <span class="o">-</span> <span class="nx">selected</span><span class="p">.</span><span class="nx">outerHeight</span><span class="p">();</span></div><div class='line' id='LC168'>				<span class="nx">list</span><span class="p">.</span><span class="nx">scrollTop</span><span class="p">(</span><span class="nx">topOffset</span><span class="p">);</span></div><div class='line' id='LC169'>			<span class="p">}</span> <span class="k">else</span> <span class="p">{</span></div><div class='line' id='LC170'>				<span class="nx">list</span><span class="p">.</span><span class="nx">scrollTop</span><span class="p">(</span><span class="mi">0</span><span class="p">);</span></div><div class='line' id='LC171'>			<span class="p">}</span></div><div class='line' id='LC172'><br/></div><div class='line' id='LC173'>			<span class="nx">self</span><span class="p">.</span><span class="nx">trigger</span><span class="p">(</span><span class="s1">&#39;showTimepicker&#39;</span><span class="p">);</span></div><div class='line' id='LC174'>		<span class="p">},</span></div><div class='line' id='LC175'><br/></div><div class='line' id='LC176'>		<span class="nx">hide</span><span class="o">:</span> <span class="kd">function</span><span class="p">(</span><span class="nx">e</span><span class="p">)</span></div><div class='line' id='LC177'>		<span class="p">{</span></div><div class='line' id='LC178'>			<span class="nx">$</span><span class="p">(</span><span class="s1">&#39;.ui-timepicker-list:visible&#39;</span><span class="p">).</span><span class="nx">each</span><span class="p">(</span><span class="kd">function</span><span class="p">()</span> <span class="p">{</span></div><div class='line' id='LC179'>				<span class="kd">var</span> <span class="nx">list</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="k">this</span><span class="p">);</span></div><div class='line' id='LC180'>				<span class="kd">var</span> <span class="nx">self</span> <span class="o">=</span> <span class="nx">list</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-input&#39;</span><span class="p">);</span></div><div class='line' id='LC181'>				<span class="kd">var</span> <span class="nx">settings</span> <span class="o">=</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-settings&#39;</span><span class="p">);</span></div><div class='line' id='LC182'><br/></div><div class='line' id='LC183'>				<span class="k">if</span> <span class="p">(</span><span class="nx">settings</span> <span class="o">&amp;&amp;</span> <span class="nx">settings</span><span class="p">.</span><span class="nx">selectOnBlur</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC184'>					<span class="nx">_selectValue</span><span class="p">(</span><span class="nx">self</span><span class="p">);</span></div><div class='line' id='LC185'>				<span class="p">}</span></div><div class='line' id='LC186'><br/></div><div class='line' id='LC187'>				<span class="nx">list</span><span class="p">.</span><span class="nx">hide</span><span class="p">();</span></div><div class='line' id='LC188'>				<span class="nx">self</span><span class="p">.</span><span class="nx">trigger</span><span class="p">(</span><span class="s1">&#39;hideTimepicker&#39;</span><span class="p">);</span></div><div class='line' id='LC189'>			<span class="p">});</span></div><div class='line' id='LC190'>		<span class="p">},</span></div><div class='line' id='LC191'><br/></div><div class='line' id='LC192'>		<span class="nx">option</span><span class="o">:</span> <span class="kd">function</span><span class="p">(</span><span class="nx">key</span><span class="p">,</span> <span class="nx">value</span><span class="p">)</span></div><div class='line' id='LC193'>		<span class="p">{</span></div><div class='line' id='LC194'>			<span class="kd">var</span> <span class="nx">self</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="k">this</span><span class="p">);</span></div><div class='line' id='LC195'>			<span class="kd">var</span> <span class="nx">settings</span> <span class="o">=</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-settings&#39;</span><span class="p">);</span></div><div class='line' id='LC196'>			<span class="kd">var</span> <span class="nx">list</span> <span class="o">=</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-list&#39;</span><span class="p">);</span></div><div class='line' id='LC197'><br/></div><div class='line' id='LC198'>			<span class="k">if</span> <span class="p">(</span><span class="k">typeof</span> <span class="nx">key</span> <span class="o">==</span> <span class="s1">&#39;object&#39;</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC199'>				<span class="nx">settings</span> <span class="o">=</span> <span class="nx">$</span><span class="p">.</span><span class="nx">extend</span><span class="p">(</span><span class="nx">settings</span><span class="p">,</span> <span class="nx">key</span><span class="p">);</span></div><div class='line' id='LC200'><br/></div><div class='line' id='LC201'>			<span class="p">}</span> <span class="k">else</span> <span class="k">if</span> <span class="p">(</span><span class="k">typeof</span> <span class="nx">key</span> <span class="o">==</span> <span class="s1">&#39;string&#39;</span> <span class="o">&amp;&amp;</span> <span class="k">typeof</span> <span class="nx">value</span> <span class="o">!=</span> <span class="s1">&#39;undefined&#39;</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC202'>				<span class="nx">settings</span><span class="p">[</span><span class="nx">key</span><span class="p">]</span> <span class="o">=</span> <span class="nx">value</span><span class="p">;</span></div><div class='line' id='LC203'><br/></div><div class='line' id='LC204'>			<span class="p">}</span> <span class="k">else</span> <span class="k">if</span> <span class="p">(</span><span class="k">typeof</span> <span class="nx">key</span> <span class="o">==</span> <span class="s1">&#39;string&#39;</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC205'>				<span class="k">return</span> <span class="nx">settings</span><span class="p">[</span><span class="nx">key</span><span class="p">];</span></div><div class='line' id='LC206'>			<span class="p">}</span></div><div class='line' id='LC207'><br/></div><div class='line' id='LC208'>			<span class="k">if</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">minTime</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC209'>				<span class="nx">settings</span><span class="p">.</span><span class="nx">minTime</span> <span class="o">=</span> <span class="nx">_time2int</span><span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">minTime</span><span class="p">);</span></div><div class='line' id='LC210'>			<span class="p">}</span></div><div class='line' id='LC211'><br/></div><div class='line' id='LC212'>			<span class="k">if</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">maxTime</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC213'>				<span class="nx">settings</span><span class="p">.</span><span class="nx">maxTime</span> <span class="o">=</span> <span class="nx">_time2int</span><span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">maxTime</span><span class="p">);</span></div><div class='line' id='LC214'>			<span class="p">}</span></div><div class='line' id='LC215'><br/></div><div class='line' id='LC216'>			<span class="k">if</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">durationTime</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC217'>				<span class="nx">settings</span><span class="p">.</span><span class="nx">durationTime</span> <span class="o">=</span> <span class="nx">_time2int</span><span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">durationTime</span><span class="p">);</span></div><div class='line' id='LC218'>			<span class="p">}</span></div><div class='line' id='LC219'><br/></div><div class='line' id='LC220'>			<span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-settings&#39;</span><span class="p">,</span> <span class="nx">settings</span><span class="p">);</span></div><div class='line' id='LC221'><br/></div><div class='line' id='LC222'>			<span class="k">if</span> <span class="p">(</span><span class="nx">list</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC223'>				<span class="nx">list</span><span class="p">.</span><span class="nx">remove</span><span class="p">();</span></div><div class='line' id='LC224'>				<span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-list&#39;</span><span class="p">,</span> <span class="kc">false</span><span class="p">);</span></div><div class='line' id='LC225'>			<span class="p">}</span></div><div class='line' id='LC226'><br/></div><div class='line' id='LC227'>		<span class="p">},</span></div><div class='line' id='LC228'><br/></div><div class='line' id='LC229'>		<span class="nx">getSecondsFromMidnight</span><span class="o">:</span> <span class="kd">function</span><span class="p">()</span></div><div class='line' id='LC230'>		<span class="p">{</span></div><div class='line' id='LC231'>			<span class="k">return</span> <span class="nx">_time2int</span><span class="p">(</span><span class="nx">$</span><span class="p">(</span><span class="k">this</span><span class="p">).</span><span class="nx">val</span><span class="p">());</span></div><div class='line' id='LC232'>		<span class="p">},</span></div><div class='line' id='LC233'><br/></div><div class='line' id='LC234'>		<span class="nx">getTime</span><span class="o">:</span> <span class="kd">function</span><span class="p">()</span></div><div class='line' id='LC235'>		<span class="p">{</span></div><div class='line' id='LC236'>			<span class="k">return</span> <span class="k">new</span> <span class="nb">Date</span><span class="p">(</span><span class="nx">_baseDate</span><span class="p">.</span><span class="nx">valueOf</span><span class="p">()</span> <span class="o">+</span> <span class="p">(</span><span class="nx">_time2int</span><span class="p">(</span><span class="nx">$</span><span class="p">(</span><span class="k">this</span><span class="p">).</span><span class="nx">val</span><span class="p">())</span><span class="o">*</span><span class="mi">1000</span><span class="p">));</span></div><div class='line' id='LC237'>		<span class="p">},</span></div><div class='line' id='LC238'><br/></div><div class='line' id='LC239'>		<span class="nx">setTime</span><span class="o">:</span> <span class="kd">function</span><span class="p">(</span><span class="nx">value</span><span class="p">)</span></div><div class='line' id='LC240'>		<span class="p">{</span></div><div class='line' id='LC241'>			<span class="kd">var</span> <span class="nx">self</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="k">this</span><span class="p">);</span></div><div class='line' id='LC242'>			<span class="kd">var</span> <span class="nx">prettyTime</span> <span class="o">=</span> <span class="nx">_int2time</span><span class="p">(</span><span class="nx">_time2int</span><span class="p">(</span><span class="nx">value</span><span class="p">),</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-settings&#39;</span><span class="p">).</span><span class="nx">timeFormat</span><span class="p">);</span></div><div class='line' id='LC243'>			<span class="nx">self</span><span class="p">.</span><span class="nx">val</span><span class="p">(</span><span class="nx">prettyTime</span><span class="p">);</span></div><div class='line' id='LC244'>		<span class="p">},</span></div><div class='line' id='LC245'><br/></div><div class='line' id='LC246'>		<span class="nx">remove</span><span class="o">:</span> <span class="kd">function</span><span class="p">()</span></div><div class='line' id='LC247'>		<span class="p">{</span></div><div class='line' id='LC248'>			<span class="kd">var</span> <span class="nx">self</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="k">this</span><span class="p">);</span></div><div class='line' id='LC249'><br/></div><div class='line' id='LC250'>			<span class="c1">// check if this element is a timepicker</span></div><div class='line' id='LC251'>			<span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nx">self</span><span class="p">.</span><span class="nx">hasClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-input&#39;</span><span class="p">))</span> <span class="p">{</span></div><div class='line' id='LC252'>				<span class="k">return</span><span class="p">;</span></div><div class='line' id='LC253'>			<span class="p">}</span></div><div class='line' id='LC254'><br/></div><div class='line' id='LC255'>			<span class="nx">self</span><span class="p">.</span><span class="nx">removeAttr</span><span class="p">(</span><span class="s1">&#39;autocomplete&#39;</span><span class="p">,</span> <span class="s1">&#39;off&#39;</span><span class="p">);</span></div><div class='line' id='LC256'>			<span class="nx">self</span><span class="p">.</span><span class="nx">removeClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-input&#39;</span><span class="p">);</span></div><div class='line' id='LC257'>			<span class="nx">self</span><span class="p">.</span><span class="nx">removeData</span><span class="p">(</span><span class="s1">&#39;timepicker-settings&#39;</span><span class="p">);</span></div><div class='line' id='LC258'>			<span class="nx">self</span><span class="p">.</span><span class="nx">off</span><span class="p">(</span><span class="s1">&#39;.timepicker&#39;</span><span class="p">);</span></div><div class='line' id='LC259'><br/></div><div class='line' id='LC260'>			<span class="c1">// timepicker-list won&#39;t be present unless the user has interacted with this timepicker</span></div><div class='line' id='LC261'>			<span class="k">if</span> <span class="p">(</span><span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-list&#39;</span><span class="p">))</span> <span class="p">{</span></div><div class='line' id='LC262'>				<span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-list&#39;</span><span class="p">).</span><span class="nx">remove</span><span class="p">();</span></div><div class='line' id='LC263'>			<span class="p">}</span></div><div class='line' id='LC264'><br/></div><div class='line' id='LC265'>			<span class="nx">self</span><span class="p">.</span><span class="nx">removeData</span><span class="p">(</span><span class="s1">&#39;timepicker-list&#39;</span><span class="p">);</span></div><div class='line' id='LC266'>		<span class="p">}</span></div><div class='line' id='LC267'>	<span class="p">};</span></div><div class='line' id='LC268'><br/></div><div class='line' id='LC269'>	<span class="c1">// private methods</span></div><div class='line' id='LC270'><br/></div><div class='line' id='LC271'>	<span class="kd">function</span> <span class="nx">_render</span><span class="p">(</span><span class="nx">self</span><span class="p">)</span></div><div class='line' id='LC272'>	<span class="p">{</span></div><div class='line' id='LC273'>		<span class="kd">var</span> <span class="nx">settings</span> <span class="o">=</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-settings&#39;</span><span class="p">);</span></div><div class='line' id='LC274'>		<span class="kd">var</span> <span class="nx">list</span> <span class="o">=</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-list&#39;</span><span class="p">);</span></div><div class='line' id='LC275'><br/></div><div class='line' id='LC276'>		<span class="k">if</span> <span class="p">(</span><span class="nx">list</span> <span class="o">&amp;&amp;</span> <span class="nx">list</span><span class="p">.</span><span class="nx">length</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC277'>			<span class="nx">list</span><span class="p">.</span><span class="nx">remove</span><span class="p">();</span></div><div class='line' id='LC278'>			<span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-list&#39;</span><span class="p">,</span> <span class="kc">false</span><span class="p">);</span></div><div class='line' id='LC279'>		<span class="p">}</span></div><div class='line' id='LC280'><br/></div><div class='line' id='LC281'>		<span class="nx">list</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="s1">&#39;&lt;ul /&gt;&#39;</span><span class="p">);</span></div><div class='line' id='LC282'>		<span class="nx">list</span><span class="p">.</span><span class="nx">attr</span><span class="p">(</span><span class="s1">&#39;tabindex&#39;</span><span class="p">,</span> <span class="o">-</span><span class="mi">1</span><span class="p">);</span></div><div class='line' id='LC283'>		<span class="nx">list</span><span class="p">.</span><span class="nx">addClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-list&#39;</span><span class="p">);</span></div><div class='line' id='LC284'>		<span class="k">if</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">className</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC285'>			<span class="nx">list</span><span class="p">.</span><span class="nx">addClass</span><span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">className</span><span class="p">);</span></div><div class='line' id='LC286'>		<span class="p">}</span></div><div class='line' id='LC287'><br/></div><div class='line' id='LC288'>		<span class="nx">list</span><span class="p">.</span><span class="nx">css</span><span class="p">({</span><span class="s1">&#39;display&#39;</span><span class="o">:</span><span class="s1">&#39;none&#39;</span><span class="p">,</span> <span class="s1">&#39;position&#39;</span><span class="o">:</span> <span class="s1">&#39;absolute&#39;</span> <span class="p">});</span></div><div class='line' id='LC289'><br/></div><div class='line' id='LC290'>		<span class="k">if</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">minTime</span> <span class="o">!==</span> <span class="kc">null</span> <span class="o">&amp;&amp;</span> <span class="nx">settings</span><span class="p">.</span><span class="nx">showDuration</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC291'>			<span class="nx">list</span><span class="p">.</span><span class="nx">addClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-with-duration&#39;</span><span class="p">);</span></div><div class='line' id='LC292'>		<span class="p">}</span></div><div class='line' id='LC293'><br/></div><div class='line' id='LC294'>		<span class="kd">var</span> <span class="nx">durStart</span> <span class="o">=</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">durationTime</span> <span class="o">!==</span> <span class="kc">null</span><span class="p">)</span> <span class="o">?</span> <span class="nx">settings</span><span class="p">.</span><span class="nx">durationTime</span> <span class="o">:</span> <span class="nx">settings</span><span class="p">.</span><span class="nx">minTime</span><span class="p">;</span></div><div class='line' id='LC295'>		<span class="kd">var</span> <span class="nx">start</span> <span class="o">=</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">minTime</span> <span class="o">!==</span> <span class="kc">null</span><span class="p">)</span> <span class="o">?</span> <span class="nx">settings</span><span class="p">.</span><span class="nx">minTime</span> <span class="o">:</span> <span class="mi">0</span><span class="p">;</span></div><div class='line' id='LC296'>		<span class="kd">var</span> <span class="nx">end</span> <span class="o">=</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">maxTime</span> <span class="o">!==</span> <span class="kc">null</span><span class="p">)</span> <span class="o">?</span> <span class="nx">settings</span><span class="p">.</span><span class="nx">maxTime</span> <span class="o">:</span> <span class="p">(</span><span class="nx">start</span> <span class="o">+</span> <span class="nx">_ONE_DAY</span> <span class="o">-</span> <span class="mi">1</span><span class="p">);</span></div><div class='line' id='LC297'><br/></div><div class='line' id='LC298'>		<span class="k">if</span> <span class="p">(</span><span class="nx">end</span> <span class="o">&lt;=</span> <span class="nx">start</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC299'>			<span class="c1">// make sure the end time is greater than start time, otherwise there will be no list to show</span></div><div class='line' id='LC300'>			<span class="nx">end</span> <span class="o">+=</span> <span class="nx">_ONE_DAY</span><span class="p">;</span></div><div class='line' id='LC301'>		<span class="p">}</span></div><div class='line' id='LC302'><br/></div><div class='line' id='LC303'>		<span class="k">for</span> <span class="p">(</span><span class="kd">var</span> <span class="nx">i</span><span class="o">=</span><span class="nx">start</span><span class="p">;</span> <span class="nx">i</span> <span class="o">&lt;=</span> <span class="nx">end</span><span class="p">;</span> <span class="nx">i</span> <span class="o">+=</span> <span class="nx">settings</span><span class="p">.</span><span class="nx">step</span><span class="o">*</span><span class="mi">60</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC304'>			<span class="kd">var</span> <span class="nx">timeInt</span> <span class="o">=</span> <span class="nx">i</span><span class="o">%</span><span class="nx">_ONE_DAY</span><span class="p">;</span></div><div class='line' id='LC305'>			<span class="kd">var</span> <span class="nx">row</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="s1">&#39;&lt;li /&gt;&#39;</span><span class="p">);</span></div><div class='line' id='LC306'>			<span class="nx">row</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;time&#39;</span><span class="p">,</span> <span class="nx">timeInt</span><span class="p">);</span></div><div class='line' id='LC307'>			<span class="nx">row</span><span class="p">.</span><span class="nx">text</span><span class="p">(</span><span class="nx">_int2time</span><span class="p">(</span><span class="nx">timeInt</span><span class="p">,</span> <span class="nx">settings</span><span class="p">.</span><span class="nx">timeFormat</span><span class="p">));</span></div><div class='line' id='LC308'><br/></div><div class='line' id='LC309'>			<span class="k">if</span> <span class="p">(</span><span class="nx">settings</span><span class="p">.</span><span class="nx">minTime</span> <span class="o">!==</span> <span class="kc">null</span> <span class="o">&amp;&amp;</span> <span class="nx">settings</span><span class="p">.</span><span class="nx">showDuration</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC310'>				<span class="kd">var</span> <span class="nx">duration</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="s1">&#39;&lt;span /&gt;&#39;</span><span class="p">);</span></div><div class='line' id='LC311'>				<span class="nx">duration</span><span class="p">.</span><span class="nx">addClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-duration&#39;</span><span class="p">);</span></div><div class='line' id='LC312'>				<span class="nx">duration</span><span class="p">.</span><span class="nx">text</span><span class="p">(</span><span class="s1">&#39; (&#39;</span><span class="o">+</span><span class="nx">_int2duration</span><span class="p">(</span><span class="nx">i</span> <span class="o">-</span> <span class="nx">durStart</span><span class="p">)</span><span class="o">+</span><span class="s1">&#39;)&#39;</span><span class="p">);</span></div><div class='line' id='LC313'>				<span class="nx">row</span><span class="p">.</span><span class="nx">append</span><span class="p">(</span><span class="nx">duration</span><span class="p">);</span></div><div class='line' id='LC314'>			<span class="p">}</span></div><div class='line' id='LC315'><br/></div><div class='line' id='LC316'>			<span class="nx">list</span><span class="p">.</span><span class="nx">append</span><span class="p">(</span><span class="nx">row</span><span class="p">);</span></div><div class='line' id='LC317'>		<span class="p">}</span></div><div class='line' id='LC318'><br/></div><div class='line' id='LC319'>		<span class="nx">list</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-input&#39;</span><span class="p">,</span> <span class="nx">self</span><span class="p">);</span></div><div class='line' id='LC320'>		<span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-list&#39;</span><span class="p">,</span> <span class="nx">list</span><span class="p">);</span></div><div class='line' id='LC321'><br/></div><div class='line' id='LC322'>		<span class="kd">var</span> <span class="nx">appendTo</span> <span class="o">=</span> <span class="nx">settings</span><span class="p">.</span><span class="nx">appendTo</span><span class="p">;</span></div><div class='line' id='LC323'>		<span class="k">if</span> <span class="p">(</span><span class="k">typeof</span> <span class="nx">appendTo</span> <span class="o">===</span> <span class="s1">&#39;string&#39;</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC324'>			<span class="nx">appendTo</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="nx">appendTo</span><span class="p">);</span></div><div class='line' id='LC325'>		<span class="p">}</span> <span class="k">else</span> <span class="k">if</span> <span class="p">(</span><span class="k">typeof</span> <span class="nx">appendTo</span> <span class="o">===</span> <span class="s1">&#39;function&#39;</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC326'>			<span class="nx">appendTo</span> <span class="o">=</span> <span class="nx">appendTo</span><span class="p">(</span><span class="nx">self</span><span class="p">);</span></div><div class='line' id='LC327'>		<span class="p">}</span></div><div class='line' id='LC328'>		<span class="nx">appendTo</span><span class="p">.</span><span class="nx">append</span><span class="p">(</span><span class="nx">list</span><span class="p">);</span></div><div class='line' id='LC329'>		<span class="nx">_setSelected</span><span class="p">(</span><span class="nx">self</span><span class="p">,</span> <span class="nx">list</span><span class="p">);</span></div><div class='line' id='LC330'><br/></div><div class='line' id='LC331'>		<span class="nx">list</span><span class="p">.</span><span class="nx">on</span><span class="p">(</span><span class="s1">&#39;click&#39;</span><span class="p">,</span> <span class="s1">&#39;li&#39;</span><span class="p">,</span> <span class="kd">function</span><span class="p">(</span><span class="nx">e</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC332'>			<span class="nx">self</span><span class="p">.</span><span class="nx">addClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-hideme&#39;</span><span class="p">);</span></div><div class='line' id='LC333'>			<span class="nx">self</span><span class="p">[</span><span class="mi">0</span><span class="p">].</span><span class="nx">focus</span><span class="p">();</span></div><div class='line' id='LC334'><br/></div><div class='line' id='LC335'>			<span class="c1">// make sure only the clicked row is selected</span></div><div class='line' id='LC336'>			<span class="nx">list</span><span class="p">.</span><span class="nx">find</span><span class="p">(</span><span class="s1">&#39;li&#39;</span><span class="p">).</span><span class="nx">removeClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC337'>			<span class="nx">$</span><span class="p">(</span><span class="k">this</span><span class="p">).</span><span class="nx">addClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC338'><br/></div><div class='line' id='LC339'>			<span class="nx">_selectValue</span><span class="p">(</span><span class="nx">self</span><span class="p">);</span></div><div class='line' id='LC340'>			<span class="nx">list</span><span class="p">.</span><span class="nx">hide</span><span class="p">();</span></div><div class='line' id='LC341'>		<span class="p">});</span></div><div class='line' id='LC342'>	<span class="p">}</span></div><div class='line' id='LC343'><br/></div><div class='line' id='LC344'>	<span class="kd">function</span> <span class="nx">_generateBaseDate</span><span class="p">()</span></div><div class='line' id='LC345'>	<span class="p">{</span></div><div class='line' id='LC346'>		<span class="kd">var</span> <span class="nx">_baseDate</span> <span class="o">=</span> <span class="k">new</span> <span class="nb">Date</span><span class="p">();</span></div><div class='line' id='LC347'>		<span class="kd">var</span> <span class="nx">_currentTimezoneOffset</span> <span class="o">=</span> <span class="nx">_baseDate</span><span class="p">.</span><span class="nx">getTimezoneOffset</span><span class="p">()</span><span class="o">*</span><span class="mi">60000</span><span class="p">;</span></div><div class='line' id='LC348'>		<span class="nx">_baseDate</span><span class="p">.</span><span class="nx">setHours</span><span class="p">(</span><span class="mi">0</span><span class="p">);</span> <span class="nx">_baseDate</span><span class="p">.</span><span class="nx">setMinutes</span><span class="p">(</span><span class="mi">0</span><span class="p">);</span> <span class="nx">_baseDate</span><span class="p">.</span><span class="nx">setSeconds</span><span class="p">(</span><span class="mi">0</span><span class="p">);</span></div><div class='line' id='LC349'>		<span class="kd">var</span> <span class="nx">_baseDateTimezoneOffset</span> <span class="o">=</span> <span class="nx">_baseDate</span><span class="p">.</span><span class="nx">getTimezoneOffset</span><span class="p">()</span><span class="o">*</span><span class="mi">60000</span><span class="p">;</span></div><div class='line' id='LC350'><br/></div><div class='line' id='LC351'>		<span class="k">return</span> <span class="k">new</span> <span class="nb">Date</span><span class="p">(</span><span class="nx">_baseDate</span><span class="p">.</span><span class="nx">valueOf</span><span class="p">()</span> <span class="o">-</span> <span class="nx">_baseDateTimezoneOffset</span> <span class="o">+</span> <span class="nx">_currentTimezoneOffset</span><span class="p">);</span></div><div class='line' id='LC352'>	<span class="p">}</span></div><div class='line' id='LC353'><br/></div><div class='line' id='LC354'>	<span class="kd">function</span> <span class="nx">_findRow</span><span class="p">(</span><span class="nx">self</span><span class="p">,</span> <span class="nx">list</span><span class="p">,</span> <span class="nx">value</span><span class="p">)</span></div><div class='line' id='LC355'>	<span class="p">{</span></div><div class='line' id='LC356'>		<span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nx">value</span> <span class="o">&amp;&amp;</span> <span class="nx">value</span> <span class="o">!==</span> <span class="mi">0</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC357'>			<span class="k">return</span> <span class="kc">false</span><span class="p">;</span></div><div class='line' id='LC358'>		<span class="p">}</span></div><div class='line' id='LC359'><br/></div><div class='line' id='LC360'>		<span class="kd">var</span> <span class="nx">settings</span> <span class="o">=</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-settings&#39;</span><span class="p">);</span></div><div class='line' id='LC361'>		<span class="kd">var</span> <span class="nx">out</span> <span class="o">=</span> <span class="kc">false</span><span class="p">;</span></div><div class='line' id='LC362'><br/></div><div class='line' id='LC363'>		<span class="c1">// loop through the menu items</span></div><div class='line' id='LC364'>		<span class="nx">list</span><span class="p">.</span><span class="nx">find</span><span class="p">(</span><span class="s1">&#39;li&#39;</span><span class="p">).</span><span class="nx">each</span><span class="p">(</span><span class="kd">function</span><span class="p">(</span><span class="nx">i</span><span class="p">,</span> <span class="nx">obj</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC365'>			<span class="kd">var</span> <span class="nx">jObj</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="nx">obj</span><span class="p">);</span></div><div class='line' id='LC366'><br/></div><div class='line' id='LC367'>			<span class="c1">// check if the value is less than half a step from each row</span></div><div class='line' id='LC368'>			<span class="k">if</span> <span class="p">(</span><span class="nb">Math</span><span class="p">.</span><span class="nx">abs</span><span class="p">(</span><span class="nx">jObj</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;time&#39;</span><span class="p">)</span> <span class="o">-</span> <span class="nx">value</span><span class="p">)</span> <span class="o">&lt;=</span> <span class="nx">settings</span><span class="p">.</span><span class="nx">step</span><span class="o">*</span><span class="mi">30</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC369'>				<span class="nx">out</span> <span class="o">=</span> <span class="nx">jObj</span><span class="p">;</span></div><div class='line' id='LC370'>				<span class="k">return</span> <span class="kc">false</span><span class="p">;</span></div><div class='line' id='LC371'>			<span class="p">}</span></div><div class='line' id='LC372'>		<span class="p">});</span></div><div class='line' id='LC373'><br/></div><div class='line' id='LC374'>		<span class="k">return</span> <span class="nx">out</span><span class="p">;</span></div><div class='line' id='LC375'>	<span class="p">}</span></div><div class='line' id='LC376'><br/></div><div class='line' id='LC377'>	<span class="kd">function</span> <span class="nx">_setSelected</span><span class="p">(</span><span class="nx">self</span><span class="p">,</span> <span class="nx">list</span><span class="p">)</span></div><div class='line' id='LC378'>	<span class="p">{</span></div><div class='line' id='LC379'>		<span class="kd">var</span> <span class="nx">timeValue</span> <span class="o">=</span> <span class="nx">_time2int</span><span class="p">(</span><span class="nx">self</span><span class="p">.</span><span class="nx">val</span><span class="p">());</span></div><div class='line' id='LC380'><br/></div><div class='line' id='LC381'>		<span class="kd">var</span> <span class="nx">selected</span> <span class="o">=</span> <span class="nx">_findRow</span><span class="p">(</span><span class="nx">self</span><span class="p">,</span> <span class="nx">list</span><span class="p">,</span> <span class="nx">timeValue</span><span class="p">);</span></div><div class='line' id='LC382'>		<span class="k">if</span> <span class="p">(</span><span class="nx">selected</span><span class="p">)</span> <span class="nx">selected</span><span class="p">.</span><span class="nx">addClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC383'>	<span class="p">}</span></div><div class='line' id='LC384'><br/></div><div class='line' id='LC385'><br/></div><div class='line' id='LC386'>	<span class="kd">function</span> <span class="nx">_formatValue</span><span class="p">()</span></div><div class='line' id='LC387'>	<span class="p">{</span></div><div class='line' id='LC388'>		<span class="k">if</span> <span class="p">(</span><span class="k">this</span><span class="p">.</span><span class="nx">value</span> <span class="o">===</span> <span class="s1">&#39;&#39;</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC389'>			<span class="k">return</span><span class="p">;</span></div><div class='line' id='LC390'>		<span class="p">}</span></div><div class='line' id='LC391'><br/></div><div class='line' id='LC392'>		<span class="kd">var</span> <span class="nx">self</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="k">this</span><span class="p">);</span></div><div class='line' id='LC393'>		<span class="kd">var</span> <span class="nx">timeInt</span> <span class="o">=</span> <span class="nx">_time2int</span><span class="p">(</span><span class="k">this</span><span class="p">.</span><span class="nx">value</span><span class="p">);</span></div><div class='line' id='LC394'><br/></div><div class='line' id='LC395'>		<span class="k">if</span> <span class="p">(</span><span class="nx">timeInt</span> <span class="o">===</span> <span class="kc">null</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC396'>			<span class="nx">self</span><span class="p">.</span><span class="nx">trigger</span><span class="p">(</span><span class="s1">&#39;timeFormatError&#39;</span><span class="p">);</span></div><div class='line' id='LC397'>			<span class="k">return</span><span class="p">;</span></div><div class='line' id='LC398'>		<span class="p">}</span></div><div class='line' id='LC399'><br/></div><div class='line' id='LC400'>		<span class="kd">var</span> <span class="nx">prettyTime</span> <span class="o">=</span> <span class="nx">_int2time</span><span class="p">(</span><span class="nx">timeInt</span><span class="p">,</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-settings&#39;</span><span class="p">).</span><span class="nx">timeFormat</span><span class="p">);</span></div><div class='line' id='LC401'>		<span class="nx">self</span><span class="p">.</span><span class="nx">val</span><span class="p">(</span><span class="nx">prettyTime</span><span class="p">);</span></div><div class='line' id='LC402'>	<span class="p">}</span></div><div class='line' id='LC403'><br/></div><div class='line' id='LC404'>	<span class="kd">function</span> <span class="nx">_keyhandler</span><span class="p">(</span><span class="nx">e</span><span class="p">)</span></div><div class='line' id='LC405'>	<span class="p">{</span></div><div class='line' id='LC406'>		<span class="kd">var</span> <span class="nx">self</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="k">this</span><span class="p">);</span></div><div class='line' id='LC407'>		<span class="kd">var</span> <span class="nx">list</span> <span class="o">=</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-list&#39;</span><span class="p">);</span></div><div class='line' id='LC408'><br/></div><div class='line' id='LC409'>		<span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nx">list</span><span class="p">.</span><span class="nx">is</span><span class="p">(</span><span class="s1">&#39;:visible&#39;</span><span class="p">))</span> <span class="p">{</span></div><div class='line' id='LC410'>			<span class="k">if</span> <span class="p">(</span><span class="nx">e</span><span class="p">.</span><span class="nx">keyCode</span> <span class="o">==</span> <span class="mi">40</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC411'>				<span class="nx">self</span><span class="p">.</span><span class="nx">focus</span><span class="p">();</span></div><div class='line' id='LC412'>			<span class="p">}</span> <span class="k">else</span> <span class="p">{</span></div><div class='line' id='LC413'>				<span class="k">return</span> <span class="kc">true</span><span class="p">;</span></div><div class='line' id='LC414'>			<span class="p">}</span></div><div class='line' id='LC415'>		<span class="p">}</span></div><div class='line' id='LC416'><br/></div><div class='line' id='LC417'>		<span class="k">switch</span> <span class="p">(</span><span class="nx">e</span><span class="p">.</span><span class="nx">keyCode</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC418'><br/></div><div class='line' id='LC419'>			<span class="k">case</span> <span class="mi">13</span><span class="o">:</span> <span class="c1">// return</span></div><div class='line' id='LC420'>				<span class="nx">_selectValue</span><span class="p">(</span><span class="nx">self</span><span class="p">);</span></div><div class='line' id='LC421'>				<span class="nx">methods</span><span class="p">.</span><span class="nx">hide</span><span class="p">.</span><span class="nx">apply</span><span class="p">(</span><span class="k">this</span><span class="p">);</span></div><div class='line' id='LC422'>				<span class="nx">e</span><span class="p">.</span><span class="nx">preventDefault</span><span class="p">();</span></div><div class='line' id='LC423'>				<span class="k">return</span> <span class="kc">false</span><span class="p">;</span></div><div class='line' id='LC424'><br/></div><div class='line' id='LC425'>			<span class="k">case</span> <span class="mi">38</span><span class="o">:</span> <span class="c1">// up</span></div><div class='line' id='LC426'>				<span class="kd">var</span> <span class="nx">selected</span> <span class="o">=</span> <span class="nx">list</span><span class="p">.</span><span class="nx">find</span><span class="p">(</span><span class="s1">&#39;.ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC427'><br/></div><div class='line' id='LC428'>				<span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nx">selected</span><span class="p">.</span><span class="nx">length</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC429'>					<span class="nx">list</span><span class="p">.</span><span class="nx">children</span><span class="p">().</span><span class="nx">each</span><span class="p">(</span><span class="kd">function</span><span class="p">(</span><span class="nx">i</span><span class="p">,</span> <span class="nx">obj</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC430'>						<span class="k">if</span> <span class="p">(</span><span class="nx">$</span><span class="p">(</span><span class="nx">obj</span><span class="p">).</span><span class="nx">position</span><span class="p">().</span><span class="nx">top</span> <span class="o">&gt;</span> <span class="mi">0</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC431'>							<span class="nx">selected</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="nx">obj</span><span class="p">);</span></div><div class='line' id='LC432'>							<span class="k">return</span> <span class="kc">false</span><span class="p">;</span></div><div class='line' id='LC433'>						<span class="p">}</span></div><div class='line' id='LC434'>					<span class="p">});</span></div><div class='line' id='LC435'>					<span class="nx">selected</span><span class="p">.</span><span class="nx">addClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC436'><br/></div><div class='line' id='LC437'>				<span class="p">}</span> <span class="k">else</span> <span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nx">selected</span><span class="p">.</span><span class="nx">is</span><span class="p">(</span><span class="s1">&#39;:first-child&#39;</span><span class="p">))</span> <span class="p">{</span></div><div class='line' id='LC438'>					<span class="nx">selected</span><span class="p">.</span><span class="nx">removeClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC439'>					<span class="nx">selected</span><span class="p">.</span><span class="nx">prev</span><span class="p">().</span><span class="nx">addClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC440'><br/></div><div class='line' id='LC441'>					<span class="k">if</span> <span class="p">(</span><span class="nx">selected</span><span class="p">.</span><span class="nx">prev</span><span class="p">().</span><span class="nx">position</span><span class="p">().</span><span class="nx">top</span> <span class="o">&lt;</span> <span class="nx">selected</span><span class="p">.</span><span class="nx">outerHeight</span><span class="p">())</span> <span class="p">{</span></div><div class='line' id='LC442'>						<span class="nx">list</span><span class="p">.</span><span class="nx">scrollTop</span><span class="p">(</span><span class="nx">list</span><span class="p">.</span><span class="nx">scrollTop</span><span class="p">()</span> <span class="o">-</span> <span class="nx">selected</span><span class="p">.</span><span class="nx">outerHeight</span><span class="p">());</span></div><div class='line' id='LC443'>					<span class="p">}</span></div><div class='line' id='LC444'>				<span class="p">}</span></div><div class='line' id='LC445'><br/></div><div class='line' id='LC446'>				<span class="k">break</span><span class="p">;</span></div><div class='line' id='LC447'><br/></div><div class='line' id='LC448'>			<span class="k">case</span> <span class="mi">40</span><span class="o">:</span> <span class="c1">// down</span></div><div class='line' id='LC449'>				<span class="nx">selected</span> <span class="o">=</span> <span class="nx">list</span><span class="p">.</span><span class="nx">find</span><span class="p">(</span><span class="s1">&#39;.ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC450'><br/></div><div class='line' id='LC451'>				<span class="k">if</span> <span class="p">(</span><span class="nx">selected</span><span class="p">.</span><span class="nx">length</span> <span class="o">===</span> <span class="mi">0</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC452'>					<span class="nx">list</span><span class="p">.</span><span class="nx">children</span><span class="p">().</span><span class="nx">each</span><span class="p">(</span><span class="kd">function</span><span class="p">(</span><span class="nx">i</span><span class="p">,</span> <span class="nx">obj</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC453'>						<span class="k">if</span> <span class="p">(</span><span class="nx">$</span><span class="p">(</span><span class="nx">obj</span><span class="p">).</span><span class="nx">position</span><span class="p">().</span><span class="nx">top</span> <span class="o">&gt;</span> <span class="mi">0</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC454'>							<span class="nx">selected</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="nx">obj</span><span class="p">);</span></div><div class='line' id='LC455'>							<span class="k">return</span> <span class="kc">false</span><span class="p">;</span></div><div class='line' id='LC456'>						<span class="p">}</span></div><div class='line' id='LC457'>					<span class="p">});</span></div><div class='line' id='LC458'><br/></div><div class='line' id='LC459'>					<span class="nx">selected</span><span class="p">.</span><span class="nx">addClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC460'>				<span class="p">}</span> <span class="k">else</span> <span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nx">selected</span><span class="p">.</span><span class="nx">is</span><span class="p">(</span><span class="s1">&#39;:last-child&#39;</span><span class="p">))</span> <span class="p">{</span></div><div class='line' id='LC461'>					<span class="nx">selected</span><span class="p">.</span><span class="nx">removeClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC462'>					<span class="nx">selected</span><span class="p">.</span><span class="nx">next</span><span class="p">().</span><span class="nx">addClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC463'><br/></div><div class='line' id='LC464'>					<span class="k">if</span> <span class="p">(</span><span class="nx">selected</span><span class="p">.</span><span class="nx">next</span><span class="p">().</span><span class="nx">position</span><span class="p">().</span><span class="nx">top</span> <span class="o">+</span> <span class="mi">2</span><span class="o">*</span><span class="nx">selected</span><span class="p">.</span><span class="nx">outerHeight</span><span class="p">()</span> <span class="o">&gt;</span> <span class="nx">list</span><span class="p">.</span><span class="nx">outerHeight</span><span class="p">())</span> <span class="p">{</span></div><div class='line' id='LC465'>						<span class="nx">list</span><span class="p">.</span><span class="nx">scrollTop</span><span class="p">(</span><span class="nx">list</span><span class="p">.</span><span class="nx">scrollTop</span><span class="p">()</span> <span class="o">+</span> <span class="nx">selected</span><span class="p">.</span><span class="nx">outerHeight</span><span class="p">());</span></div><div class='line' id='LC466'>					<span class="p">}</span></div><div class='line' id='LC467'>				<span class="p">}</span></div><div class='line' id='LC468'><br/></div><div class='line' id='LC469'>				<span class="k">break</span><span class="p">;</span></div><div class='line' id='LC470'><br/></div><div class='line' id='LC471'>			<span class="k">case</span> <span class="mi">27</span><span class="o">:</span> <span class="c1">// escape</span></div><div class='line' id='LC472'>				<span class="nx">list</span><span class="p">.</span><span class="nx">find</span><span class="p">(</span><span class="s1">&#39;li&#39;</span><span class="p">).</span><span class="nx">removeClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC473'>				<span class="nx">list</span><span class="p">.</span><span class="nx">hide</span><span class="p">();</span></div><div class='line' id='LC474'>				<span class="k">break</span><span class="p">;</span></div><div class='line' id='LC475'><br/></div><div class='line' id='LC476'>			<span class="k">case</span> <span class="mi">9</span><span class="o">:</span> <span class="c1">//tab</span></div><div class='line' id='LC477'>				<span class="nx">methods</span><span class="p">.</span><span class="nx">hide</span><span class="p">();</span></div><div class='line' id='LC478'>				<span class="k">break</span><span class="p">;</span></div><div class='line' id='LC479'><br/></div><div class='line' id='LC480'>			<span class="k">case</span> <span class="mi">16</span><span class="o">:</span></div><div class='line' id='LC481'>			<span class="k">case</span> <span class="mi">17</span><span class="o">:</span></div><div class='line' id='LC482'>			<span class="k">case</span> <span class="mi">18</span><span class="o">:</span></div><div class='line' id='LC483'>			<span class="k">case</span> <span class="mi">19</span><span class="o">:</span></div><div class='line' id='LC484'>			<span class="k">case</span> <span class="mi">20</span><span class="o">:</span></div><div class='line' id='LC485'>			<span class="k">case</span> <span class="mi">33</span><span class="o">:</span></div><div class='line' id='LC486'>			<span class="k">case</span> <span class="mi">34</span><span class="o">:</span></div><div class='line' id='LC487'>			<span class="k">case</span> <span class="mi">35</span><span class="o">:</span></div><div class='line' id='LC488'>			<span class="k">case</span> <span class="mi">36</span><span class="o">:</span></div><div class='line' id='LC489'>			<span class="k">case</span> <span class="mi">37</span><span class="o">:</span></div><div class='line' id='LC490'>			<span class="k">case</span> <span class="mi">39</span><span class="o">:</span></div><div class='line' id='LC491'>			<span class="k">case</span> <span class="mi">45</span><span class="o">:</span></div><div class='line' id='LC492'>				<span class="k">return</span><span class="p">;</span></div><div class='line' id='LC493'><br/></div><div class='line' id='LC494'>			<span class="k">default</span><span class="o">:</span></div><div class='line' id='LC495'>				<span class="nx">list</span><span class="p">.</span><span class="nx">find</span><span class="p">(</span><span class="s1">&#39;li&#39;</span><span class="p">).</span><span class="nx">removeClass</span><span class="p">(</span><span class="s1">&#39;ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC496'>				<span class="k">return</span><span class="p">;</span></div><div class='line' id='LC497'>		<span class="p">}</span></div><div class='line' id='LC498'>	<span class="p">}</span></div><div class='line' id='LC499'><br/></div><div class='line' id='LC500'>	<span class="kd">function</span> <span class="nx">_selectValue</span><span class="p">(</span><span class="nx">self</span><span class="p">)</span></div><div class='line' id='LC501'>	<span class="p">{</span></div><div class='line' id='LC502'>		<span class="kd">var</span> <span class="nx">settings</span> <span class="o">=</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-settings&#39;</span><span class="p">);</span></div><div class='line' id='LC503'>		<span class="kd">var</span> <span class="nx">list</span> <span class="o">=</span> <span class="nx">self</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;timepicker-list&#39;</span><span class="p">);</span></div><div class='line' id='LC504'>		<span class="kd">var</span> <span class="nx">timeValue</span> <span class="o">=</span> <span class="kc">null</span><span class="p">;</span></div><div class='line' id='LC505'><br/></div><div class='line' id='LC506'>		<span class="kd">var</span> <span class="nx">cursor</span> <span class="o">=</span> <span class="nx">list</span><span class="p">.</span><span class="nx">find</span><span class="p">(</span><span class="s1">&#39;.ui-timepicker-selected&#39;</span><span class="p">);</span></div><div class='line' id='LC507'><br/></div><div class='line' id='LC508'>		<span class="k">if</span> <span class="p">(</span><span class="nx">cursor</span><span class="p">.</span><span class="nx">length</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC509'>			<span class="c1">// selected value found</span></div><div class='line' id='LC510'>			<span class="nx">timeValue</span> <span class="o">=</span> <span class="nx">cursor</span><span class="p">.</span><span class="nx">data</span><span class="p">(</span><span class="s1">&#39;time&#39;</span><span class="p">);</span></div><div class='line' id='LC511'><br/></div><div class='line' id='LC512'>		<span class="p">}</span> <span class="k">else</span> <span class="k">if</span> <span class="p">(</span><span class="nx">self</span><span class="p">.</span><span class="nx">val</span><span class="p">())</span> <span class="p">{</span></div><div class='line' id='LC513'><br/></div><div class='line' id='LC514'>			<span class="c1">// no selected value; fall back on input value</span></div><div class='line' id='LC515'>			<span class="nx">timeValue</span> <span class="o">=</span> <span class="nx">_time2int</span><span class="p">(</span><span class="nx">self</span><span class="p">.</span><span class="nx">val</span><span class="p">());</span></div><div class='line' id='LC516'><br/></div><div class='line' id='LC517'>			<span class="nx">_setSelected</span><span class="p">(</span><span class="nx">self</span><span class="p">,</span> <span class="nx">list</span><span class="p">);</span></div><div class='line' id='LC518'>		<span class="p">}</span></div><div class='line' id='LC519'><br/></div><div class='line' id='LC520'>		<span class="k">if</span> <span class="p">(</span><span class="nx">timeValue</span> <span class="o">!==</span> <span class="kc">null</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC521'>			<span class="kd">var</span> <span class="nx">timeString</span> <span class="o">=</span> <span class="nx">_int2time</span><span class="p">(</span><span class="nx">timeValue</span><span class="p">,</span> <span class="nx">settings</span><span class="p">.</span><span class="nx">timeFormat</span><span class="p">);</span></div><div class='line' id='LC522'>			<span class="nx">self</span><span class="p">.</span><span class="nx">attr</span><span class="p">(</span><span class="s1">&#39;value&#39;</span><span class="p">,</span> <span class="nx">timeString</span><span class="p">);</span></div><div class='line' id='LC523'>		<span class="p">}</span></div><div class='line' id='LC524'><br/></div><div class='line' id='LC525'>		<span class="nx">self</span><span class="p">.</span><span class="nx">trigger</span><span class="p">(</span><span class="s1">&#39;change&#39;</span><span class="p">).</span><span class="nx">trigger</span><span class="p">(</span><span class="s1">&#39;changeTime&#39;</span><span class="p">);</span></div><div class='line' id='LC526'>	<span class="p">}</span></div><div class='line' id='LC527'><br/></div><div class='line' id='LC528'>	<span class="kd">function</span> <span class="nx">_int2duration</span><span class="p">(</span><span class="nx">seconds</span><span class="p">)</span></div><div class='line' id='LC529'>	<span class="p">{</span></div><div class='line' id='LC530'>		<span class="kd">var</span> <span class="nx">minutes</span> <span class="o">=</span> <span class="nb">Math</span><span class="p">.</span><span class="nx">round</span><span class="p">(</span><span class="nx">seconds</span><span class="o">/</span><span class="mi">60</span><span class="p">);</span></div><div class='line' id='LC531'>		<span class="kd">var</span> <span class="nx">duration</span><span class="p">;</span></div><div class='line' id='LC532'><br/></div><div class='line' id='LC533'>		<span class="k">if</span> <span class="p">(</span><span class="nx">minutes</span> <span class="o">&lt;</span> <span class="mi">60</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC534'>			<span class="nx">duration</span> <span class="o">=</span> <span class="p">[</span><span class="nx">minutes</span><span class="p">,</span> <span class="nx">_lang</span><span class="p">.</span><span class="nx">mins</span><span class="p">];</span></div><div class='line' id='LC535'>		<span class="p">}</span> <span class="k">else</span> <span class="k">if</span> <span class="p">(</span><span class="nx">minutes</span> <span class="o">==</span> <span class="mi">60</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC536'>			<span class="nx">duration</span> <span class="o">=</span> <span class="p">[</span><span class="s1">&#39;1&#39;</span><span class="p">,</span> <span class="nx">_lang</span><span class="p">.</span><span class="nx">hr</span><span class="p">];</span></div><div class='line' id='LC537'>		<span class="p">}</span> <span class="k">else</span> <span class="p">{</span></div><div class='line' id='LC538'>			<span class="kd">var</span> <span class="nx">hours</span> <span class="o">=</span> <span class="p">(</span><span class="nx">minutes</span><span class="o">/</span><span class="mi">60</span><span class="p">).</span><span class="nx">toFixed</span><span class="p">(</span><span class="mi">1</span><span class="p">);</span></div><div class='line' id='LC539'>			<span class="k">if</span> <span class="p">(</span><span class="nx">_lang</span><span class="p">.</span><span class="nx">decimal</span> <span class="o">!=</span> <span class="s1">&#39;.&#39;</span><span class="p">)</span> <span class="nx">hours</span> <span class="o">=</span> <span class="nx">hours</span><span class="p">.</span><span class="nx">replace</span><span class="p">(</span><span class="s1">&#39;.&#39;</span><span class="p">,</span> <span class="nx">_lang</span><span class="p">.</span><span class="nx">decimal</span><span class="p">);</span></div><div class='line' id='LC540'>			<span class="nx">duration</span> <span class="o">=</span> <span class="p">[</span><span class="nx">hours</span><span class="p">,</span> <span class="nx">_lang</span><span class="p">.</span><span class="nx">hrs</span><span class="p">];</span></div><div class='line' id='LC541'>		<span class="p">}</span></div><div class='line' id='LC542'><br/></div><div class='line' id='LC543'>		<span class="k">return</span> <span class="nx">duration</span><span class="p">.</span><span class="nx">join</span><span class="p">(</span><span class="s1">&#39; &#39;</span><span class="p">);</span></div><div class='line' id='LC544'>	<span class="p">}</span></div><div class='line' id='LC545'><br/></div><div class='line' id='LC546'>	<span class="kd">function</span> <span class="nx">_int2time</span><span class="p">(</span><span class="nx">seconds</span><span class="p">,</span> <span class="nx">format</span><span class="p">)</span></div><div class='line' id='LC547'>	<span class="p">{</span></div><div class='line' id='LC548'>		<span class="k">if</span> <span class="p">(</span><span class="nx">seconds</span> <span class="o">===</span> <span class="kc">null</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC549'>			<span class="k">return</span><span class="p">;</span></div><div class='line' id='LC550'>		<span class="p">}</span></div><div class='line' id='LC551'><br/></div><div class='line' id='LC552'>		<span class="kd">var</span> <span class="nx">time</span> <span class="o">=</span> <span class="k">new</span> <span class="nb">Date</span><span class="p">(</span><span class="nx">_baseDate</span><span class="p">.</span><span class="nx">valueOf</span><span class="p">()</span> <span class="o">+</span> <span class="p">(</span><span class="nx">seconds</span><span class="o">*</span><span class="mi">1000</span><span class="p">));</span></div><div class='line' id='LC553'>		<span class="kd">var</span> <span class="nx">output</span> <span class="o">=</span> <span class="s1">&#39;&#39;</span><span class="p">;</span></div><div class='line' id='LC554'>		<span class="kd">var</span> <span class="nx">hour</span><span class="p">,</span> <span class="nx">code</span><span class="p">;</span></div><div class='line' id='LC555'><br/></div><div class='line' id='LC556'>		<span class="k">for</span> <span class="p">(</span><span class="kd">var</span> <span class="nx">i</span><span class="o">=</span><span class="mi">0</span><span class="p">;</span> <span class="nx">i</span><span class="o">&lt;</span><span class="nx">format</span><span class="p">.</span><span class="nx">length</span><span class="p">;</span> <span class="nx">i</span><span class="o">++</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC557'><br/></div><div class='line' id='LC558'>			<span class="nx">code</span> <span class="o">=</span> <span class="nx">format</span><span class="p">.</span><span class="nx">charAt</span><span class="p">(</span><span class="nx">i</span><span class="p">);</span></div><div class='line' id='LC559'>			<span class="k">switch</span> <span class="p">(</span><span class="nx">code</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC560'><br/></div><div class='line' id='LC561'>				<span class="k">case</span> <span class="s1">&#39;a&#39;</span><span class="o">:</span></div><div class='line' id='LC562'>					<span class="nx">output</span> <span class="o">+=</span> <span class="p">(</span><span class="nx">time</span><span class="p">.</span><span class="nx">getHours</span><span class="p">()</span> <span class="o">&gt;</span> <span class="mi">11</span><span class="p">)</span> <span class="o">?</span> <span class="s1">&#39;pm&#39;</span> <span class="o">:</span> <span class="s1">&#39;am&#39;</span><span class="p">;</span></div><div class='line' id='LC563'>					<span class="k">break</span><span class="p">;</span></div><div class='line' id='LC564'><br/></div><div class='line' id='LC565'>				<span class="k">case</span> <span class="s1">&#39;A&#39;</span><span class="o">:</span></div><div class='line' id='LC566'>					<span class="nx">output</span> <span class="o">+=</span> <span class="p">(</span><span class="nx">time</span><span class="p">.</span><span class="nx">getHours</span><span class="p">()</span> <span class="o">&gt;</span> <span class="mi">11</span><span class="p">)</span> <span class="o">?</span> <span class="s1">&#39;PM&#39;</span> <span class="o">:</span> <span class="s1">&#39;AM&#39;</span><span class="p">;</span></div><div class='line' id='LC567'>					<span class="k">break</span><span class="p">;</span></div><div class='line' id='LC568'><br/></div><div class='line' id='LC569'>				<span class="k">case</span> <span class="s1">&#39;g&#39;</span><span class="o">:</span></div><div class='line' id='LC570'>					<span class="nx">hour</span> <span class="o">=</span> <span class="nx">time</span><span class="p">.</span><span class="nx">getHours</span><span class="p">()</span> <span class="o">%</span> <span class="mi">12</span><span class="p">;</span></div><div class='line' id='LC571'>					<span class="nx">output</span> <span class="o">+=</span> <span class="p">(</span><span class="nx">hour</span> <span class="o">===</span> <span class="mi">0</span><span class="p">)</span> <span class="o">?</span> <span class="s1">&#39;12&#39;</span> <span class="o">:</span> <span class="nx">hour</span><span class="p">;</span></div><div class='line' id='LC572'>					<span class="k">break</span><span class="p">;</span></div><div class='line' id='LC573'><br/></div><div class='line' id='LC574'>				<span class="k">case</span> <span class="s1">&#39;G&#39;</span><span class="o">:</span></div><div class='line' id='LC575'>					<span class="nx">output</span> <span class="o">+=</span> <span class="nx">time</span><span class="p">.</span><span class="nx">getHours</span><span class="p">();</span></div><div class='line' id='LC576'>					<span class="k">break</span><span class="p">;</span></div><div class='line' id='LC577'><br/></div><div class='line' id='LC578'>				<span class="k">case</span> <span class="s1">&#39;h&#39;</span><span class="o">:</span></div><div class='line' id='LC579'>					<span class="nx">hour</span> <span class="o">=</span> <span class="nx">time</span><span class="p">.</span><span class="nx">getHours</span><span class="p">()</span> <span class="o">%</span> <span class="mi">12</span><span class="p">;</span></div><div class='line' id='LC580'><br/></div><div class='line' id='LC581'>					<span class="k">if</span> <span class="p">(</span><span class="nx">hour</span> <span class="o">!==</span> <span class="mi">0</span> <span class="o">&amp;&amp;</span> <span class="nx">hour</span> <span class="o">&lt;</span> <span class="mi">10</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC582'>						<span class="nx">hour</span> <span class="o">=</span> <span class="s1">&#39;0&#39;</span><span class="o">+</span><span class="nx">hour</span><span class="p">;</span></div><div class='line' id='LC583'>					<span class="p">}</span></div><div class='line' id='LC584'><br/></div><div class='line' id='LC585'>					<span class="nx">output</span> <span class="o">+=</span> <span class="p">(</span><span class="nx">hour</span> <span class="o">===</span> <span class="mi">0</span><span class="p">)</span> <span class="o">?</span> <span class="s1">&#39;12&#39;</span> <span class="o">:</span> <span class="nx">hour</span><span class="p">;</span></div><div class='line' id='LC586'>					<span class="k">break</span><span class="p">;</span></div><div class='line' id='LC587'><br/></div><div class='line' id='LC588'>				<span class="k">case</span> <span class="s1">&#39;H&#39;</span><span class="o">:</span></div><div class='line' id='LC589'>					<span class="nx">hour</span> <span class="o">=</span> <span class="nx">time</span><span class="p">.</span><span class="nx">getHours</span><span class="p">();</span></div><div class='line' id='LC590'>					<span class="nx">output</span> <span class="o">+=</span> <span class="p">(</span><span class="nx">hour</span> <span class="o">&gt;</span> <span class="mi">9</span><span class="p">)</span> <span class="o">?</span> <span class="nx">hour</span> <span class="o">:</span> <span class="s1">&#39;0&#39;</span><span class="o">+</span><span class="nx">hour</span><span class="p">;</span></div><div class='line' id='LC591'>					<span class="k">break</span><span class="p">;</span></div><div class='line' id='LC592'><br/></div><div class='line' id='LC593'>				<span class="k">case</span> <span class="s1">&#39;i&#39;</span><span class="o">:</span></div><div class='line' id='LC594'>					<span class="kd">var</span> <span class="nx">minutes</span> <span class="o">=</span> <span class="nx">time</span><span class="p">.</span><span class="nx">getMinutes</span><span class="p">();</span></div><div class='line' id='LC595'>					<span class="nx">output</span> <span class="o">+=</span> <span class="p">(</span><span class="nx">minutes</span> <span class="o">&gt;</span> <span class="mi">9</span><span class="p">)</span> <span class="o">?</span> <span class="nx">minutes</span> <span class="o">:</span> <span class="s1">&#39;0&#39;</span><span class="o">+</span><span class="nx">minutes</span><span class="p">;</span></div><div class='line' id='LC596'>					<span class="k">break</span><span class="p">;</span></div><div class='line' id='LC597'><br/></div><div class='line' id='LC598'>				<span class="k">case</span> <span class="s1">&#39;s&#39;</span><span class="o">:</span></div><div class='line' id='LC599'>					<span class="nx">seconds</span> <span class="o">=</span> <span class="nx">time</span><span class="p">.</span><span class="nx">getSeconds</span><span class="p">();</span></div><div class='line' id='LC600'>					<span class="nx">output</span> <span class="o">+=</span> <span class="p">(</span><span class="nx">seconds</span> <span class="o">&gt;</span> <span class="mi">9</span><span class="p">)</span> <span class="o">?</span> <span class="nx">seconds</span> <span class="o">:</span> <span class="s1">&#39;0&#39;</span><span class="o">+</span><span class="nx">seconds</span><span class="p">;</span></div><div class='line' id='LC601'>					<span class="k">break</span><span class="p">;</span></div><div class='line' id='LC602'><br/></div><div class='line' id='LC603'>				<span class="k">default</span><span class="o">:</span></div><div class='line' id='LC604'>					<span class="nx">output</span> <span class="o">+=</span> <span class="nx">code</span><span class="p">;</span></div><div class='line' id='LC605'>			<span class="p">}</span></div><div class='line' id='LC606'>		<span class="p">}</span></div><div class='line' id='LC607'><br/></div><div class='line' id='LC608'>		<span class="k">return</span> <span class="nx">output</span><span class="p">;</span></div><div class='line' id='LC609'>	<span class="p">}</span></div><div class='line' id='LC610'><br/></div><div class='line' id='LC611'>	<span class="kd">function</span> <span class="nx">_time2int</span><span class="p">(</span><span class="nx">timeString</span><span class="p">)</span></div><div class='line' id='LC612'>	<span class="p">{</span></div><div class='line' id='LC613'>		<span class="k">if</span> <span class="p">(</span><span class="nx">timeString</span> <span class="o">===</span> <span class="s1">&#39;&#39;</span><span class="p">)</span> <span class="k">return</span> <span class="kc">null</span><span class="p">;</span></div><div class='line' id='LC614'>		<span class="k">if</span> <span class="p">(</span><span class="nx">timeString</span><span class="o">+</span><span class="mi">0</span> <span class="o">==</span> <span class="nx">timeString</span><span class="p">)</span> <span class="k">return</span> <span class="nx">timeString</span><span class="p">;</span></div><div class='line' id='LC615'><br/></div><div class='line' id='LC616'>		<span class="k">if</span> <span class="p">(</span><span class="k">typeof</span><span class="p">(</span><span class="nx">timeString</span><span class="p">)</span> <span class="o">==</span> <span class="s1">&#39;object&#39;</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC617'>			<span class="nx">timeString</span> <span class="o">=</span> <span class="nx">timeString</span><span class="p">.</span><span class="nx">getHours</span><span class="p">()</span><span class="o">+</span><span class="s1">&#39;:&#39;</span><span class="o">+</span><span class="nx">timeString</span><span class="p">.</span><span class="nx">getMinutes</span><span class="p">()</span><span class="o">+</span><span class="s1">&#39;:&#39;</span><span class="o">+</span><span class="nx">timeString</span><span class="p">.</span><span class="nx">getSeconds</span><span class="p">();</span></div><div class='line' id='LC618'>		<span class="p">}</span></div><div class='line' id='LC619'><br/></div><div class='line' id='LC620'>		<span class="kd">var</span> <span class="nx">d</span> <span class="o">=</span> <span class="k">new</span> <span class="nb">Date</span><span class="p">(</span><span class="mi">0</span><span class="p">);</span></div><div class='line' id='LC621'>		<span class="kd">var</span> <span class="nx">time</span> <span class="o">=</span> <span class="nx">timeString</span><span class="p">.</span><span class="nx">toLowerCase</span><span class="p">().</span><span class="nx">match</span><span class="p">(</span><span class="sr">/(\d{1,2})(?::(\d{1,2}))?(?::(\d{2}))?\s*([pa]?)/</span><span class="p">);</span></div><div class='line' id='LC622'><br/></div><div class='line' id='LC623'>		<span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nx">time</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC624'>			<span class="k">return</span> <span class="kc">null</span><span class="p">;</span></div><div class='line' id='LC625'>		<span class="p">}</span></div><div class='line' id='LC626'><br/></div><div class='line' id='LC627'>		<span class="kd">var</span> <span class="nx">hour</span> <span class="o">=</span> <span class="nb">parseInt</span><span class="p">(</span><span class="nx">time</span><span class="p">[</span><span class="mi">1</span><span class="p">]</span><span class="o">*</span><span class="mi">1</span><span class="p">,</span> <span class="mi">10</span><span class="p">);</span></div><div class='line' id='LC628'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="kd">var</span> <span class="nx">hours</span><span class="p">;</span></div><div class='line' id='LC629'><br/></div><div class='line' id='LC630'>		<span class="k">if</span> <span class="p">(</span><span class="nx">time</span><span class="p">[</span><span class="mi">4</span><span class="p">])</span> <span class="p">{</span></div><div class='line' id='LC631'>			<span class="k">if</span> <span class="p">(</span><span class="nx">hour</span> <span class="o">==</span> <span class="mi">12</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC632'>				<span class="nx">hours</span> <span class="o">=</span> <span class="p">(</span><span class="nx">time</span><span class="p">[</span><span class="mi">4</span><span class="p">]</span> <span class="o">==</span> <span class="s1">&#39;p&#39;</span><span class="p">)</span> <span class="o">?</span> <span class="mi">12</span> <span class="o">:</span> <span class="mi">0</span><span class="p">;</span></div><div class='line' id='LC633'>			<span class="p">}</span> <span class="k">else</span> <span class="p">{</span></div><div class='line' id='LC634'>				<span class="nx">hours</span> <span class="o">=</span> <span class="p">(</span><span class="nx">hour</span> <span class="o">+</span> <span class="p">(</span><span class="nx">time</span><span class="p">[</span><span class="mi">4</span><span class="p">]</span> <span class="o">==</span> <span class="s1">&#39;p&#39;</span> <span class="o">?</span> <span class="mi">12</span> <span class="o">:</span> <span class="mi">0</span><span class="p">));</span></div><div class='line' id='LC635'>			<span class="p">}</span></div><div class='line' id='LC636'><br/></div><div class='line' id='LC637'>		<span class="p">}</span> <span class="k">else</span> <span class="p">{</span></div><div class='line' id='LC638'>			<span class="nx">hours</span> <span class="o">=</span> <span class="nx">hour</span><span class="p">;</span></div><div class='line' id='LC639'>		<span class="p">}</span></div><div class='line' id='LC640'><br/></div><div class='line' id='LC641'>		<span class="kd">var</span> <span class="nx">minutes</span> <span class="o">=</span> <span class="p">(</span> <span class="nx">time</span><span class="p">[</span><span class="mi">2</span><span class="p">]</span><span class="o">*</span><span class="mi">1</span> <span class="o">||</span> <span class="mi">0</span> <span class="p">);</span></div><div class='line' id='LC642'>		<span class="kd">var</span> <span class="nx">seconds</span> <span class="o">=</span> <span class="p">(</span> <span class="nx">time</span><span class="p">[</span><span class="mi">3</span><span class="p">]</span><span class="o">*</span><span class="mi">1</span> <span class="o">||</span> <span class="mi">0</span> <span class="p">);</span></div><div class='line' id='LC643'>		<span class="k">return</span> <span class="nx">hours</span><span class="o">*</span><span class="mi">3600</span> <span class="o">+</span> <span class="nx">minutes</span><span class="o">*</span><span class="mi">60</span> <span class="o">+</span> <span class="nx">seconds</span><span class="p">;</span></div><div class='line' id='LC644'>	<span class="p">}</span></div><div class='line' id='LC645'><br/></div><div class='line' id='LC646'>	<span class="c1">// Plugin entry</span></div><div class='line' id='LC647'>	<span class="nx">$</span><span class="p">.</span><span class="nx">fn</span><span class="p">.</span><span class="nx">timepicker</span> <span class="o">=</span> <span class="kd">function</span><span class="p">(</span><span class="nx">method</span><span class="p">)</span></div><div class='line' id='LC648'>	<span class="p">{</span></div><div class='line' id='LC649'>		<span class="k">if</span><span class="p">(</span><span class="nx">methods</span><span class="p">[</span><span class="nx">method</span><span class="p">])</span> <span class="p">{</span> <span class="k">return</span> <span class="nx">methods</span><span class="p">[</span><span class="nx">method</span><span class="p">].</span><span class="nx">apply</span><span class="p">(</span><span class="k">this</span><span class="p">,</span> <span class="nb">Array</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">slice</span><span class="p">.</span><span class="nx">call</span><span class="p">(</span><span class="nx">arguments</span><span class="p">,</span> <span class="mi">1</span><span class="p">));</span> <span class="p">}</span></div><div class='line' id='LC650'>		<span class="k">else</span> <span class="k">if</span><span class="p">(</span><span class="k">typeof</span> <span class="nx">method</span> <span class="o">===</span> <span class="s2">&quot;object&quot;</span> <span class="o">||</span> <span class="o">!</span><span class="nx">method</span><span class="p">)</span> <span class="p">{</span> <span class="k">return</span> <span class="nx">methods</span><span class="p">.</span><span class="nx">init</span><span class="p">.</span><span class="nx">apply</span><span class="p">(</span><span class="k">this</span><span class="p">,</span> <span class="nx">arguments</span><span class="p">);</span> <span class="p">}</span></div><div class='line' id='LC651'>		<span class="k">else</span> <span class="p">{</span> <span class="nx">$</span><span class="p">.</span><span class="nx">error</span><span class="p">(</span><span class="s2">&quot;Method &quot;</span><span class="o">+</span> <span class="nx">method</span> <span class="o">+</span> <span class="s2">&quot; does not exist on jQuery.timepicker&quot;</span><span class="p">);</span> <span class="p">}</span></div><div class='line' id='LC652'>	<span class="p">};</span></div><div class='line' id='LC653'><span class="p">}));</span></div></pre></div>
          </td>
        </tr>
      </table>
  </div>

          </div>
        </div>
      </div>

      <a href="#jump-to-line" rel="facebox" data-hotkey="l" class="js-jump-to-line" style="display:none">Jump to Line</a>
      <div id="jump-to-line" style="display:none">
        <h2>Jump to Line</h2>
        <form accept-charset="UTF-8" class="js-jump-to-line-form">
          <input class="textfield js-jump-to-line-field" type="text">
          <div class="full-button">
            <button type="submit" class="classy">
              Go
            </button>
          </div>
        </form>
      </div>

    </div>
</div>

<div class="frame frame-loading large-loading-area" style="display:none;">
  <img src="https://a248.e.akamai.net/assets.github.com/images/spinners/octocat-spinner-128.gif?1347543527" height="64" width="64">
</div>

        </div>
      </div>
      <div class="context-overlay"></div>
    </div>

      <div id="footer-push"></div><!-- hack for sticky footer -->
    </div><!-- end of wrapper - hack for sticky footer -->

      <!-- footer -->
      <div id="footer">
  <div class="container clearfix">

      <dl class="footer_nav">
        <dt>GitHub</dt>
        <dd><a href="https://github.com/about">About us</a></dd>
        <dd><a href="https://github.com/blog">Blog</a></dd>
        <dd><a href="https://github.com/contact">Contact &amp; support</a></dd>
        <dd><a href="http://enterprise.github.com/">GitHub Enterprise</a></dd>
        <dd><a href="http://status.github.com/">Site status</a></dd>
      </dl>

      <dl class="footer_nav">
        <dt>Applications</dt>
        <dd><a href="http://mac.github.com/">GitHub for Mac</a></dd>
        <dd><a href="http://windows.github.com/">GitHub for Windows</a></dd>
        <dd><a href="http://eclipse.github.com/">GitHub for Eclipse</a></dd>
        <dd><a href="http://mobile.github.com/">GitHub mobile apps</a></dd>
      </dl>

      <dl class="footer_nav">
        <dt>Services</dt>
        <dd><a href="http://get.gaug.es/">Gauges: Web analytics</a></dd>
        <dd><a href="http://speakerdeck.com">Speaker Deck: Presentations</a></dd>
        <dd><a href="https://gist.github.com">Gist: Code snippets</a></dd>
        <dd><a href="http://jobs.github.com/">Job board</a></dd>
      </dl>

      <dl class="footer_nav">
        <dt>Documentation</dt>
        <dd><a href="http://help.github.com/">GitHub Help</a></dd>
        <dd><a href="http://developer.github.com/">Developer API</a></dd>
        <dd><a href="http://github.github.com/github-flavored-markdown/">GitHub Flavored Markdown</a></dd>
        <dd><a href="http://pages.github.com/">GitHub Pages</a></dd>
      </dl>

      <dl class="footer_nav">
        <dt>More</dt>
        <dd><a href="http://training.github.com/">Training</a></dd>
        <dd><a href="https://github.com/edu">Students &amp; teachers</a></dd>
        <dd><a href="http://shop.github.com">The Shop</a></dd>
        <dd><a href="http://octodex.github.com/">The Octodex</a></dd>
      </dl>

      <hr class="footer-divider">


    <p class="right">&copy; 2012 <span title="0.07952s from fe18.rs.github.com">GitHub</span> Inc. All rights reserved.</p>
    <a class="left" href="https://github.com/">
      <span class="mega-icon mega-icon-invertocat"></span>
    </a>
    <ul id="legal">
        <li><a href="https://github.com/site/terms">Terms of Service</a></li>
        <li><a href="https://github.com/site/privacy">Privacy</a></li>
        <li><a href="https://github.com/security">Security</a></li>
    </ul>

  </div><!-- /.container -->

</div><!-- /.#footer -->


    

<div id="keyboard_shortcuts_pane" class="instapaper_ignore readability-extra" style="display:none">
  <h2>Keyboard Shortcuts <small><a href="#" class="js-see-all-keyboard-shortcuts">(see all)</a></small></h2>

  <div class="columns threecols">
    <div class="column first">
      <h3>Site wide shortcuts</h3>
      <dl class="keyboard-mappings">
        <dt>s</dt>
        <dd>Focus command bar</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>?</dt>
        <dd>Bring up this help dialog</dd>
      </dl>
    </div><!-- /.column.first -->

    <div class="column middle" style='display:none'>
      <h3>Commit list</h3>
      <dl class="keyboard-mappings">
        <dt>j</dt>
        <dd>Move selection down</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>k</dt>
        <dd>Move selection up</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>c <em>or</em> o <em>or</em> enter</dt>
        <dd>Open commit</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>y</dt>
        <dd>Expand URL to its canonical form</dd>
      </dl>
    </div><!-- /.column.first -->

    <div class="column last js-hidden-pane" style='display:none'>
      <h3>Pull request list</h3>
      <dl class="keyboard-mappings">
        <dt>j</dt>
        <dd>Move selection down</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>k</dt>
        <dd>Move selection up</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>o <em>or</em> enter</dt>
        <dd>Open issue</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt><span class="platform-mac">⌘</span><span class="platform-other">ctrl</span> <em>+</em> enter</dt>
        <dd>Submit comment</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt><span class="platform-mac">⌘</span><span class="platform-other">ctrl</span> <em>+</em> shift p</dt>
        <dd>Preview comment</dd>
      </dl>
    </div><!-- /.columns.last -->

  </div><!-- /.columns.equacols -->

  <div class="js-hidden-pane" style='display:none'>
    <div class="rule"></div>

    <h3>Issues</h3>

    <div class="columns threecols">
      <div class="column first">
        <dl class="keyboard-mappings">
          <dt>j</dt>
          <dd>Move selection down</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>k</dt>
          <dd>Move selection up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>x</dt>
          <dd>Toggle selection</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>o <em>or</em> enter</dt>
          <dd>Open issue</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt><span class="platform-mac">⌘</span><span class="platform-other">ctrl</span> <em>+</em> enter</dt>
          <dd>Submit comment</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt><span class="platform-mac">⌘</span><span class="platform-other">ctrl</span> <em>+</em> shift p</dt>
          <dd>Preview comment</dd>
        </dl>
      </div><!-- /.column.first -->
      <div class="column last">
        <dl class="keyboard-mappings">
          <dt>c</dt>
          <dd>Create issue</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>l</dt>
          <dd>Create label</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>i</dt>
          <dd>Back to inbox</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>u</dt>
          <dd>Back to issues</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>/</dt>
          <dd>Focus issues search</dd>
        </dl>
      </div>
    </div>
  </div>

  <div class="js-hidden-pane" style='display:none'>
    <div class="rule"></div>

    <h3>Issues Dashboard</h3>

    <div class="columns threecols">
      <div class="column first">
        <dl class="keyboard-mappings">
          <dt>j</dt>
          <dd>Move selection down</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>k</dt>
          <dd>Move selection up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>o <em>or</em> enter</dt>
          <dd>Open issue</dd>
        </dl>
      </div><!-- /.column.first -->
    </div>
  </div>

  <div class="js-hidden-pane" style='display:none'>
    <div class="rule"></div>

    <h3>Network Graph</h3>
    <div class="columns equacols">
      <div class="column first">
        <dl class="keyboard-mappings">
          <dt><span class="badmono">←</span> <em>or</em> h</dt>
          <dd>Scroll left</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt><span class="badmono">→</span> <em>or</em> l</dt>
          <dd>Scroll right</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt><span class="badmono">↑</span> <em>or</em> k</dt>
          <dd>Scroll up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt><span class="badmono">↓</span> <em>or</em> j</dt>
          <dd>Scroll down</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>t</dt>
          <dd>Toggle visibility of head labels</dd>
        </dl>
      </div><!-- /.column.first -->
      <div class="column last">
        <dl class="keyboard-mappings">
          <dt>shift <span class="badmono">←</span> <em>or</em> shift h</dt>
          <dd>Scroll all the way left</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>shift <span class="badmono">→</span> <em>or</em> shift l</dt>
          <dd>Scroll all the way right</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>shift <span class="badmono">↑</span> <em>or</em> shift k</dt>
          <dd>Scroll all the way up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>shift <span class="badmono">↓</span> <em>or</em> shift j</dt>
          <dd>Scroll all the way down</dd>
        </dl>
      </div><!-- /.column.last -->
    </div>
  </div>

  <div class="js-hidden-pane" >
    <div class="rule"></div>
    <div class="columns threecols">
      <div class="column first js-hidden-pane" >
        <h3>Source Code Browsing</h3>
        <dl class="keyboard-mappings">
          <dt>t</dt>
          <dd>Activates the file finder</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>l</dt>
          <dd>Jump to line</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>w</dt>
          <dd>Switch branch/tag</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>y</dt>
          <dd>Expand URL to its canonical form</dd>
        </dl>
      </div>
    </div>
  </div>

  <div class="js-hidden-pane" style='display:none'>
    <div class="rule"></div>
    <div class="columns threecols">
      <div class="column first">
        <h3>Browsing Commits</h3>
        <dl class="keyboard-mappings">
          <dt><span class="platform-mac">⌘</span><span class="platform-other">ctrl</span> <em>+</em> enter</dt>
          <dd>Submit comment</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>escape</dt>
          <dd>Close form</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>p</dt>
          <dd>Parent commit</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>o</dt>
          <dd>Other parent commit</dd>
        </dl>
      </div>
    </div>
  </div>

  <div class="js-hidden-pane" style='display:none'>
    <div class="rule"></div>
    <h3>Notifications</h3>

    <div class="columns threecols">
      <div class="column first">
        <dl class="keyboard-mappings">
          <dt>j</dt>
          <dd>Move selection down</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>k</dt>
          <dd>Move selection up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>o <em>or</em> enter</dt>
          <dd>Open notification</dd>
        </dl>
      </div><!-- /.column.first -->

      <div class="column second">
        <dl class="keyboard-mappings">
          <dt>e <em>or</em> shift i <em>or</em> y</dt>
          <dd>Mark as read</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>shift m</dt>
          <dd>Mute thread</dd>
        </dl>
      </div><!-- /.column.first -->
    </div>
  </div>

</div>

    <div id="markdown-help" class="instapaper_ignore readability-extra">
  <h2>Markdown Cheat Sheet</h2>

  <div class="cheatsheet-content">

  <div class="mod">
    <div class="col">
      <h3>Format Text</h3>
      <p>Headers</p>
      <pre>
# This is an &lt;h1&gt; tag
## This is an &lt;h2&gt; tag
###### This is an &lt;h6&gt; tag</pre>
     <p>Text styles</p>
     <pre>
*This text will be italic*
_This will also be italic_
**This text will be bold**
__This will also be bold__

*You **can** combine them*
</pre>
    </div>
    <div class="col">
      <h3>Lists</h3>
      <p>Unordered</p>
      <pre>
* Item 1
* Item 2
  * Item 2a
  * Item 2b</pre>
     <p>Ordered</p>
     <pre>
1. Item 1
2. Item 2
3. Item 3
   * Item 3a
   * Item 3b</pre>
    </div>
    <div class="col">
      <h3>Miscellaneous</h3>
      <p>Images</p>
      <pre>
![GitHub Logo](/images/logo.png)
Format: ![Alt Text](url)
</pre>
     <p>Links</p>
     <pre>
http://github.com - automatic!
[GitHub](http://github.com)</pre>
<p>Blockquotes</p>
     <pre>
As Kanye West said:

> We're living the future so
> the present is our past.
</pre>
    </div>
  </div>
  <div class="rule"></div>

  <h3>Code Examples in Markdown</h3>
  <div class="col">
      <p>Syntax highlighting with <a href="http://github.github.com/github-flavored-markdown/" title="GitHub Flavored Markdown" target="_blank">GFM</a></p>
      <pre>
```javascript
function fancyAlert(arg) {
  if(arg) {
    $.facebox({div:'#foo'})
  }
}
```</pre>
    </div>
    <div class="col">
      <p>Or, indent your code 4 spaces</p>
      <pre>
Here is a Python code example
without syntax highlighting:

    def foo:
      if not bar:
        return true</pre>
    </div>
    <div class="col">
      <p>Inline code for comments</p>
      <pre>
I think you should use an
`&lt;addr&gt;` element here instead.</pre>
    </div>
  </div>

  </div>
</div>


    <div id="ajax-error-message" class="flash flash-error">
      <span class="mini-icon mini-icon-exclamation"></span>
      Something went wrong with that request. Please try again.
      <a href="#" class="mini-icon mini-icon-remove-close ajax-error-dismiss"></a>
    </div>

    
    
    <span id='server_response_time' data-time='0.08096' data-host='fe18'></span>
    
  </body>
</html>

