

Ext.define('GestComp.app.Affichage',{
	alias:'widget.appaffichage',
	requires:['GestComp.affichage.principal.panel.Eleve'],
	extend:'Ext.Panel',
	layout:'card',
	activeItem:0,
	initComponent:function() {
		this.items=[{
				title:'Gestion d\'un élève',
				itemId:'navEleve',
				xtype:'paneleleve'
		//		xtype:'infoeleve'
		//		les itemId sont identiques aux id de navigation correspondants
		// 		(pour correspondance facile dans le changement de card)
			},{
				title:'Gestion des groupes',
				itemId:'navGroupes'		
			},{
				itemId:'navCompetences',
				title:'Gestion des compétences'
			},{
				title:'Gestion des evaluations',
				itemId:'navEvaluations'
		}];
		Ext.apply(this);
		GestComp.app.Affichage.superclass.initComponent.apply(this,arguments);
		this.eleve=this.child('#navEleve');
		this.groupes=this.child('#navGroupes');
		this.competences=this.child('#navCompetences');
		this.evaluations=this.child('#navEvaluations');
		
	}
});

Ext.define('GestComp.app.Navigation',{
	requires:['GestComp.navigation.eleves','GestComp.navigation.competences'],
	alias:'widget.appnavigation',
	extend:'Ext.Panel',	
	layout:'accordion',
	layoutConfig : {animate:true},
	title:'Navigation',
    anchor:-50,
    defaults: { bodyStyle : "overflow:auto;" },
	width:'30%',
	align:'left',
	collapsible : true,
	
	initComponent:function() {
		this.items=[{
				id:'navEleve',
				title:'Elève',		
				xtype:'grideleves',
				listeners: {
				//	juste pour l'exemple
					'expand':function() {GestComp.Message.fireEvent('message',this,'oop','ol'); }
				}
			},{
				id:'navGroupes',
				title:'Groupe',
				html:'groupes'
			},{
				id:'navCompetences',
				title:'Compétences',
				xtype:'gridcompetences'
				//html:'competences'
			},{
				id:'navEvaluations',
				title:'Evaluations',
				html:'évals'
		}],
		Ext.apply(this);
		GestComp.app.Navigation.superclass.initComponent.apply(this,arguments);
		this.eleve=this.child('#navEleve');
		this.groupes=this.child('#navGroupes');
		this.competences=this.child('#navCompetences');
		this.evaluations=this.child('#navEvaluations');	
		//this.competences.on('expand',function() {GestComp.Competences.load({params:{action:'piliers'}})},this,{single:true})
	}
	
});

Ext.define('GestComp.app.Center', {
	alias:'widget.appcenter',
	extend: 'Ext.Panel',
	layout: {
            type: 'border',
            padding: '0 5' 
    },
    defaults: {
            split: true
    },
	items:[{
		region:'west',
		xtype:'appnavigation'
	},{
		region:'center',
		xtype:'appaffichage',		
	}],
	
	initComponent:function() {
		GestComp.app.Center.superclass.initComponent.apply(this, arguments);
		
		this.affichage=this.child('appaffichage');
		this.navigation=this.child('appnavigation');

	},
	initEvents:function() {
		this.callParent();
		
		/*
		 * ajout des evenements sur expansion 
		 */
		var me=this
		// procedure de changement de card sur le panel affichage
		var changeAffichage=function(key){			
			//les itemId de affichage étant identiques aux id de navigation il suffit de faire:
			me.affichage.getLayout().setActiveItem(key)
		};		
		//changement de card pour chaque expand d'un élément de l'accordeon navigation		
		this.navigation.items.eachKey(function(key,item){
			item.on('expand',function(){
				changeAffichage(key)
				//jsute pour l'exemple				
				GestComp.Message.fireEvent('message',me.navigation,'expand',key)
			});
		});
		
		/*
		 * Actions sur navigation eleve
		 */
		smEleve=this.navigation.eleve.getSelectionModel()
		// un eleve est selectionne, on active les différents tab (une seule fois)
		
		smEleve.on('select',function(){
			me.affichage.eleve.items.eachKey(function(key,item){item.setDisabled(false)})
			},
			this,{single:true,delay:1000}
		);
		
		smEleve.on('selectionchange',this.onEleveChange,this,{test:true})

	},
	onEleveChange:function(sm,sel,options) {
		// on a selectionné un autre eleve dans le panel navigation
		// maj du titre
		if (options.test) this.affichage.eleve.updateTitle(sel[0].data)
		else console.log('rien');
 		//maj des détails
 		this.affichage.eleve.accesRapide.infosEleve.updateDetail(sel[0].data);
	}
	
	
});