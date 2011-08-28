Ext.define('GestComp.Prof.view.evaluation.Affichage',{
	//requires:['GestComp.Prof.view.eleve.Infos'],
	extend:'GestComp.Prof.view.affichage.TabPanel',
	alias:'widget.evaluation_affichage',
	title:'panel évaluation',	
	
	initComponent:function() {
		this.items=[{xtype:'panel',
			
			title:'Résultats',
			id:'tab-resultats',
			html:'grille resultats'			
		},{
			
			title:'Autres',
			id:'tab_autres',
			disabled:true
			
		}];
		
		this.callParent()
	},
	updateTitle:function(record) {
			this.setTitle(record.get('nom'));
		}
});