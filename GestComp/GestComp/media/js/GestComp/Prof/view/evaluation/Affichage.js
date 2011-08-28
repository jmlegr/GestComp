Ext.define('GestComp.Prof.view.evaluation.Affichage',{
	//requires:['GestComp.Prof.view.eleve.Infos'],
	requires:['GestComp.Prof.view.evaluation.Resultats'],
	extend:'GestComp.Prof.view.affichage.TabPanel',
	alias:'widget.evaluation_affichage',
	title:'panel évaluation',	
	
	initComponent:function() {
		this.items=[{//xtype:'panel',
			xtype:'evaluation_resultats',
			gridlockable:true,   
			title:'Résultats',
			id:'tab-resultats',
		},{
			
			title:'Autres',
			id:'tab-autres',
			disabled:true,
			tpl:'<tpl> <p><b>{nom}</b> (n°{id})</p>'+
				'<tpl if="date_evaluation"><p>effectuée le {date_evaluation:date("l d F Y")}</p></tpl>'+
				'<p> modifiée le {date_modification:date("l d F Y")}'+
				' à {date_modification:date("G:i")}</p></tpl>'
			
		}];
		
		this.callParent()
	},
	updateTitle:function(record) {
			this.setTitle(record.get('nom'));
		}
}); 