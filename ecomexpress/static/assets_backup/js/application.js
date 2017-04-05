/*global  $,Cufon,Modernizr,yepnope */
/*jslint browser:true*/

// consider performance! http://24ways.org/2011/your-jquery-now-with-less-suck
var rev = {


    init: function() {

        //bootstrap's buttons on revlets
        $('.revlet .btn').button();

        //device specific js
        rev.helpers.checkBrowserSize();

        //init the tab switcher in nav
        rev.tabs.init();
        
        rev.tooltips.init();

        //custom modals (we position the modal correctly in mobile browsers)
        rev.modals.init();

        //init the revlet actions
        rev.revlets.init();

        if (!Modernizr.nthchildn) {
            $('.main .span4:even').addClass('mless');
        }

    },
    
    tooltips: {
        
        init:function() {
         
          $('body').on('click', 'a[rel="popover"]', function(e) {
        
            e.preventDefault();
            
            //tooltip action here
        
          });
          
        }
      
    },

    modals: {

        init: function() {

            //when bootstrap fix the positioning of modals in mobile browsers this can be removed and
            //all data-rev-action="modal" can be renamed to bootstrap's data-toggle="modal"
            $('body').on('click', '[data-rev-action="modal"]',
            function(e) {
                e.preventDefault();

                if ($(this).attr('data-target') && $($(this).attr('data-target')).length) {

                    var modal = $(this).attr('data-target');

                    if ($(window).width() <= 510 && undefined !== window.pageYOffset) {
                        //mobile
                        $(modal).modal('show').css({
                            'top': 0,
                            'margin-top': window.pageYOffset + 10
                        });
                    } else {
                        //desktop
                        $(modal).modal('show');
                    }
                }

            });

        }

    },

    tabs: {

        init: function() {

            var $tabs = $('.rev-tabs');

            $tabs.on('click', 'a',
            function(e) {
                e.preventDefault();

                //ensure both large and small tab switchers match
                if (!$(this).attr('data-rev-action')) {
                    //!not create tab - change text
                    $tabs.find('a').removeClass('active').end().
                    find('a[href="' + $(this).attr('href') + '"]').addClass('active');
                    $('.small-tabs-select .dropdown-toggle > span').text($(this).text());

                    alert('Change to tab ' + $(this).attr('href'));

                }

            });

        }

    },



    revlets: {

        init: function() {

            $('.revlet').on('click', '.btn[data-rev-action]',
            function(e) {

                var action = $(this).attr('data-rev-action');

                e.preventDefault();
                
                if (typeof rev.revlets.actions[action] !== 'undefined') {
                    rev.revlets.actions[action]($(this));
                }

            });

        },

        actions: {

            togglemetrics: function($obj) {

                var $thisRevlet = $obj.parents('.revlet').eq(0),
                $metricCells = $thisRevlet.find('.mt'),
                $weekCells = $thisRevlet.find('.lw, .tw')
                $weekSpans = $weekCells.find('span'),
                $metricsSpans = $metricCells.find('span'),
                metricSpanSize = $metricsSpans.length,
                weekSpanSize = $weekSpans.length,
                spaceAvail = 0;
                

                if (!$thisRevlet.hasClass('showing-week-data')) {
                    $obj.find('i').addClass('rotate-right');
                    spaceAvail = $metricCells.eq(0).outerWidth();
                    
                    $metricsSpans.each(function(i) {

                        //slide out each metric cell
                        $(this).animate({
                            'left': -spaceAvail
                        },
                        700,
                        function() {
                            if (i + 1 === metricSpanSize) {
                                $metricCells.find('a').hide().end().hide();
                                $weekSpans.css({
                                    'left': -spaceAvail
                                });
                                $weekCells.show();

                                //slide in each week cell
                                $weekSpans.each(function(i) {
                                    $(this).animate({
                                        'left': 0
                                    },
                                    700,
                                    function() {
                                        if (i + 1 === weekSpanSize) {                                     
                                            $thisRevlet.addClass('showing-week-data');
                                        }
                                    });
                                });
                            }

                        });
                    });

                } else {
                  spaceAvail = $weekCells.eq(0).outerWidth() * 2;
                  
                  $obj.find('i').removeClass('rotate-right');  
                    
                    $weekSpans.each(function(i) {
                        //slide out each week cell
                        $(this).animate({
                            'left': -spaceAvail
                        },
                        700,
                        function() {
                            if (i + 1 === weekSpanSize) {
                                $weekCells.hide();
                                $metricCells.show();
                                $metricCells.find('span').each(function(i) {
                                    $(this).animate({
                                        'left': 0
                                    },
                                    500,
                                    function() {
                                        if (i + 1 === metricSpanSize) {
                                            //last
                                            $metricCells.find('a').fadeIn(100);
                                            $thisRevlet.removeClass('showing-week-data');
                                        }

                                    });
                                });
                            }
                        });
                    });
                }


            },

            refresh: function($obj) {

                var $thisIcon = $obj.find('i');

                $thisIcon.addClass('rotate');

                //dummy refresh
                setTimeout(function() {
                    $thisIcon.removeClass('rotate');
                    alert('Refresh complete.')
                },
                2000);

            },

            daterange: function($obj) {

                alert('Show me data over ' + $obj.attr('data-rev-action-val') + ' day[s]');

            },

            remove: function($obj) {

                alert('Remove this revlet.');

            },

            showgraph: function($obj) {

                alert('Show graph data');

            }


        }
    },

    helpers: {

        checkBrowserSize: function() {

            var w = $(window),
            wSize = {
                width: w.width(),
                height: w.height()
            };

            if (wSize.width <= 510) {
                //mobiles
                $('a[rel="popover"]').popover({
                    placement: 'bottom'
                });
            } else {
                //desktops
                $('a[rel="popover"]').popover({
                    placement: 'right'
                });
            }

        }

    }


};

