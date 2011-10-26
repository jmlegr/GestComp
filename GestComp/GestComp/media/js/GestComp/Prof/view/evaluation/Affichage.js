Ext.define('GestComp.Prof.view.evaluation.Affichage',{
	//requires:['GestComp.Prof.view.eleve.Infos'],
	requires:['GestComp.Prof.view.evaluation.Resultats'],
	extend:'GestComp.Prof.view.affichage.TabPanel',
	alias:'widget.evaluation_affichage',
	title:'panel évaluation',	
	
	initComponent:function() {
		this.tools=[{
		    type:'refresh',
		    tooltip: 'Refresh form Data',
		    // hidden:true,
		    handler: function(event, toolEl, panel){
		        // refresh logic
		    }
		},
		{
		    type:'help',
		    tooltip: 'Get Help',
		    handler: function(event, toolEl, panel){
		        // show help here
		    }
		}]
		this.deferredRender=false,
		this.items=[{
			layout:'border',
			id:'evaluation_resultats',
			items:[{
				region:'center',
				id:'grille_resultats',
				xtype:'evaluation_resultats',
			},{
				region:'east',
				id:'panel_detail',
				html:'details',
				title:'détails',
				collapsible:true,
				split:true,
			}],
			
			gridlockable:true,   
			title:'Résultats',
			id:'tab-resultats',
		},{
			layout: 'border',
			title:'Autres',
			id:'tab-autres',
			disabled:true,
			items:[{
				region:'center',flex:1,
				id:'infos_eval_general',
				tpl:new Ext.XTemplate('<tpl> <p><b>{nom}</b> (n°{id}) créée par <i>{user}</i></p>',			
				'<tpl if="date_evaluation"><p>effectuée le {date_evaluation:date("l d F Y")}</p></tpl>',
				'<p> modifiée le {date_modification:date("l d F Y")}',
				' à {date_modification:date("G:i")}</p></tpl>')
				},{
					region:'south',flex:1,
					id:'infos_eval_detail', html:'bientot ici',
					tpl: '<tpl><tpl if="note"><p><b>Notée</b></p></tpl>'+
						'Description: {description}</tpl>'
				}]
			
		}];
		
		this.callParent()
	},
	updateTitle:function(record) {
			this.setTitle(record.get('nom'));
		}
}); 