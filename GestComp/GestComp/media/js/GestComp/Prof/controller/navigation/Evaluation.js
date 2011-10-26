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
