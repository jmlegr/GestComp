Ext.define('GestComp.Prof.view.Viewport',{
	extend:'Ext.container.Viewport',
	requires:[
		'GestComp.Prof.view.affichage.Principal',
		'GestComp.Prof.view.Navigation'
	],
	layout:'border',
	initComponent:function(){	
		this.defaults={split:true,collapsible:true}
		this.items=[{
				layout:'hbox',            	
            	
				dockedItems: [{
			        xtype: 'toolbar',
			        dock: 'left',
			        items: [{
			        	text: '',
			        	tooltip:'se déconnecter',
			        	//scale   : 'large',
                        iconCls: 'icon-disconnect',
                        handler: function(){
                        	window.location="/gestcomp/logout"
                        }
                    },{
                        text: '',
                        tooltip:'Modifier le mot de passe',
                        disabled:true,
                        iconCls: 'icon-key',
                        handler: function(){
                                    }
			        }]
			    }],
            	title:'GestComp - '+user.nom+', '+user.prenom,
            	region:'north',
            	items:[{         
            		xtype:'box',
            		id:'app-header',
            		
            		html:'GestComp version beta 0.7 <span class="subtitle">Ext 4.0 Version</span>'+
            			'  ' +user.nom,
            		componentCls:'test',
            		flex:1
            	}],
            	height:75
		},{
			xtype:'navigation',
			region:'west'
		},{
			xtype:'affichage_principal',
			region:'center',
			collapsible:false
		},{
			title:'Messages',
			region:'south',
			html:'les messages'	,
			height:70
		}];
		Ext.apply(this)
		this.callParent(arguments)
	}
		
})