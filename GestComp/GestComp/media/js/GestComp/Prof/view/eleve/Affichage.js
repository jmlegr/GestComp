Ext.define('GestComp.Prof.view.eleve.Affichage',{
	requires:['GestComp.Prof.view.eleve.Infos'],
	extend:'GestComp.Prof.view.affichage.TabPanel',
	alias:'widget.eleve_affichage',
	title:'panel eleve',	
	
	initComponent:function() {
		this.items=[{
			layout:'border',
			title:'Accès rapide',
			id:'tab-accesrapide',
			items:[{
				region:'north',
				xtype:'infoseleve', 
				//html:'test',
				split:true,
				height:100,
				id:'info-eleve'
			},{
				region:'center',
				html:'valid rapide'
			}]
		},{
			xtype:'panel',
			title:'Résultats',
			id:'tab_resultat',
			disabled:true
			
		}];
		
		this.callParent()
	},
	updateTitle:function(record) {
			this.setTitle(record.get('nom').toUpperCase()+' '+Ext.String.capitalize(record.get('prenom')));
		}
});