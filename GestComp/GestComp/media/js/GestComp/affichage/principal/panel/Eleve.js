// panel informations d'un élève et validation directe
Ext.define('GestComp.affichage.principal.panel.Eleve',{
	requires:['GestComp.affichage.principal.eleve.Infos'],
	extend:'GestComp.affichage.principal.TabPanel',
	alias:'widget.paneleleve',
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
			title:'Résultats',
			disabled:true
			
		}];
		Ext.apply(this)
        GestComp.affichage.principal.panel.Eleve.superclass.initComponent.apply(this, arguments);
        this.accesRapide=this.child('#tab-accesrapide')
        this.accesRapide.infosEleve=this.accesRapide.child('infoseleve')
	},
	updateTitle:function(data) {
		this.setTitle(data.nom.toUpperCase()+' '+Ext.String.capitalize(data.prenom))
	}
});
