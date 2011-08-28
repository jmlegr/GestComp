/*
 * View: Navigation
 * Accordeon de navigation entre les différents affichages
 */
 
Ext.define('GestComp.Prof.view.Navigation',{
	requires:[
		'GestComp.Prof.view.navigation.Eleve',
		'GestComp.Prof.view.navigation.Evaluation',
		//'GestComp.navigation.competences'
	],
	alias:'widget.navigation',
	extend:'Ext.Panel',	
	layout:'accordion',
	layoutConfig : {animate:true},
	title:'Navigation',
    anchor:-50,
    defaults: { bodyStyle : "overflow:auto;" },
	width:'30%',
	align:'left',
	collapsible : true,
	activeItem:2,
	initComponent:function() {
		this.items=[{
				id:'navEleve',
				title:'Elève',		
				xtype:'navigation_eleve',				
			},{
				id:'navGroupes',
				title:'Groupe',
				html:'groupes'
			},{
				id:'navCompetences',
				title:'Compétences',
				//xtype:'gridcompetences'
				html:'competences'
			},{
				id:'navEvaluations',
				title:'Evaluations',
				xtype:'navigation_evaluation',
		}];
		this.callParent();
	}
});
