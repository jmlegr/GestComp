Ext.Loader.setConfig({enabled: true});
Ext.Loader.setPath('Ext.ux', '/smedia/js/ext-4/examples/ux');
Ext.Loader.setPath('GestComp.override', '/smedia/js/GestComp/override');
Ext.Loader.setPath('GestComp.ux', '/smedia/js/GestComp/ux');
Ext.application({
    name: 'GestComp.Prof',

    appFolder: '/smedia/js/GestComp/Prof',

	controllers:[	
		'Navigation',
		'navigation.Eleve',
		'navigation.Evaluation',
		'evaluation.Resultat'
	],
	requires:['GestComp.ux.DynamicGrid','GestComp.Prof.view.evaluation.Resultats'],
	autoCreateViewport:true,
    launch: function() {
    	// ajotu du csrf token pour django
    	Ext.Ajax.on('beforerequest', function (conn, options) {			
   			if (!(/^http:.*/.test(options.url) || /^https:.*/.test(options.url))) {
   				     if (typeof(options.headers) == "undefined") {  
       					options.headers = {'X-CSRFToken': Ext.util.Cookies.get('csrftoken')};  					  
     				} else {     					
       					options.headers.extend({'X-CSRFToken': Ext.util.Cookies.get('csrftoken')});
     				}                        
   			}
		}, this);
     
 

/*
    Ext.create('Ext.window.Window', {
    title: 'Hello',
    height: 200,
    width: 400,
    maximizable:true,
    layout: 'fit',
    items: {  // Let's put an empty grid in just to illustrate fit layout
        //xtype: 'dynamicgrid'
    	xtype:'evaluation_resultats'
    	, id:'testgrid',
        border: false,
        autoscroll:true,
        gridlockable:true,      
        
    },
    listeners:{
    	'maximize':function() {
    		//cols=[{header:'id',dataIndex:'nom',tpl:'<tpl>++{nom}--</tpl>', renderer: function(v) {console.log('v',v);return 'pp'+v}},{header:'biduel'}]
    		//console.log('rec',cols)
    		//Ext.getCmp('testgrid').reconfigure('',cols)
    		
    	}
    }
}).show();
*/
    }
});