
/*
 * view: Principal
 * card panel des différents affichages
 */
 
 Ext.define('GestComp.Prof.view.affichage.Principal',{
	alias:'widget.affichage_principal',
	requires:[
		'GestComp.Prof.view.eleve.Affichage',
		'GestComp.Prof.view.evaluation.Affichage'
		],
	extend:'Ext.Panel',
	layout:'card',
	activeItem:0,
	initComponent:function() {
		this.items=[{
				title:'Gestion d\'un élève',
				itemId:'navEleve',
				//html:'panaleleve',
				xtype:'eleve_affichage'
			},{
				title:'Gestion des groupes',
				itemId:'navGroupes'		
			},{
				itemId:'navCompetences',
				title:'Gestion des compétences'
			},{
				title:'Gestion des evaluations',
				itemId:'navEvaluations',
				xtype:'evaluation_affichage'
		}];
		this.callParent()		
	}
});
