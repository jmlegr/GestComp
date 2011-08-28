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