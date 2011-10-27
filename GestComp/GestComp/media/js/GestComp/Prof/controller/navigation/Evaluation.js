/*
 * Controller: navigation.Evaluation
 * controle les changements d'affichage quand une évaluation est sélectionnée dans le panel navigation
 */
 
Ext.define('GestComp.Prof.controller.navigation.Evaluation', {
    extend: 'Ext.app.Controller',
    views: ['navigation.Evaluation','evaluation.Affichage'],

    refs:[{ 	
    	ref:'affichage',
    	selector:'evaluation_affichage'
    },{
    	ref:'grille_resultats',
    	selector:'evaluation_affichage #grille_resultats'
    },{
    	ref:'general',
    	selector:'evaluation_affichage #tab-autres > #infos_eval_general'
    },{
    	ref:'detail',
    	selector:'evaluation_affichage #tab-autres > #infos_eval_detail'    
    }],
    
    stores:['Evaluations'],
    init: function() {
    	//calcul de la date de la rentrée pour être large, fixée au 15 aout
		var today=new Date();
		var date_rentree=new Date(today.getMonth()>=8?today.getFullYear():today.getFullYear()-1,7,15);
    	var zedate=new Date(2010,2,1);
		
		//activation des tabs
    	this.control({
    		'navigation_evaluation': {   		
    			'itemclick':{
	    			fn:this.activeTabs,
    				single:true    			
    			}
    		}
    	});
    	// mise à jour de la barre de titre, des infos élèves
    	this.control({
    		'navigation_evaluation': {   
    			'itemclick':{
    				fn:this.selectClickEvaluation,
    				buffer:1000 
    			}    			
    		}
    	});		
    	//ajout des filtres dès le premier rendu du layout
    	/* TODO: 
    	 * -ajouter les filtres au chargelment du store
    	 * 				this.getEvaluationsStore().on('load',function(st){
		 *					console.log('eval chergées',st.filters)})
		 *- Filtrage par le serveur, par défaut année en cours
    	 */
    	this.control({
    		'navigation_evaluation': {
    			load: function() {console.info('loaded')},
    			afterlayout: {
    				fn: function(t,l) {    			
    							console.log('layout',this,t,t.filters,t.filters.getFilter('date_evaluation'));
    							t.filters.addFilter({
    								type: 'date',
    								dataIndex:'date_evaluation',
    								value:{after:zedate}
    								//value:{after:date_rentree}
    							});
    							t.filters.addFilter({
    								type: 'date',
    								dataIndex:'date_modification',
    								value:{after:zedate}
    								
    							})
    							//Le filtre n'est pas appliqué sur les dates d'éval, sinon on n'afficha pas les evals sans date
    							t.filters.getFilter('date_evaluation').setActive(false);  
    							t.filters.getFilter('date_modification').setActive(true);
    				}, single:true
    			}
    		}
    	})
    	
    	//Modification de l'afficahe de l'aonglet "autre" de l'eval
    	this.control({
    		'evaluation_resultats': {
    			
    			'reconfigure':function(a,b,c,d){
    				if (this.getGrille_resultats().eval) {
    					this.getDetail().tpl.overwrite(this.getDetail().body,this.getGrille_resultats().eval)
    					this.getGeneral().tpl.overwrite(this.getGeneral().body,this.getGrille_resultats().eval)
    				} 

    			}
    		}
    	})
    	
    },
    selectClickEvaluation:function(view,record,item,index){    	
    	this.getAffichage().updateTitle(record);  
    	//console.log('tpmaplte',this.getGeneral().body)
    	//this.getGeneral().tpl.overwrite(this.getGeneral().body,record.data)
    	this.getGrille_resultats().reload(record.get('id'))
 		
 	},
 	
 	activeTabs:function() {
 		//activation des onglets lors du premier select
 		this.getAffichage().items.eachKey(function(key,item){item.setDisabled(false)})
 	}
});
