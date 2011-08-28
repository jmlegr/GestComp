	
Ext.define('GestComp.Prof',{
	requires:[
		'Ext.Ajax','Ext.util.Cookies',
		'Ext.container.Viewport',
		
		'Ext.data.Store',
		'GestComp.message',
		'GestComp.app',
	],

	
	stores:  ['eleves','competences'],
	init: function() {


		Ext.QuickTips.init();
		// ajout pour csrf
		// !!! ERREUR si Loader dynamique - pourquoi??? - faut-il mieux charger un override.js?
		Ext.Ajax.on('beforerequest', function (conn, options) {	
   			if (!(/^http:.*/.test(options.url) || /^https:.*/.test(options.url))) {
   				     if (typeof(options.headers) == "undefined") {  
  					   	console.info('beforerequest',Ext.util.Cookies.get('csrftoken'))
       					options.headers = {'X-CSRFToken': Ext.util.Cookies.get('csrftoken')};
     				} else {
     					console.info('beforerequest exten')
       					options.headers.extend({'X-CSRFToken': Ext.util.Cookies.get('csrftoken')});
     				}                        
   			}
		}, this);
		

		
		v=new Ext.container.Viewport({
            layout: 'border',
            
            id:'viewport',
            items:[{
            	layout:'hbox',            	
            	
            	id:'app-header',
            	region:'north',
            	items:[{         
            		xtype:'box',
            		
            		html:'GestComp version beta 0.7 <span class="subtitle">Ext 4.0 Version</span>'+
            			'  ' +user.nom,
            		componentCls:'test',
            		flex:1
            	},{bodyBorder:false,
            		html:'  <a href="/gestcomp/logout">Se déconnecter</a>',
            		autoWidth:true,
            	}],
            	height:50
            },{
            	region:'center',
            	border:false,
            	id:'app-center',
            	xtype:'appcenter',
            	//html:'test center'
            },{
            	region:'south',
            	id:'app-messages',
            	title:'messages',
            	collapsible: true,
            	collapseMode: 'mini',
        		xtype:'messagepanel',
        		split: true,
        		height: 75
            }]            
        });
	}
});
