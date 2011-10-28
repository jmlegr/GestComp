var po=0
Ext.define('GestComp.Prof.controller.evaluation.Resultat', {
    extend: 'Ext.app.Controller',
    views: ['navigation.Evaluation','evaluation.Affichage'],
    
    refs:[{ 	
    	ref:'affichage',
    	selector:'evaluation_affichage'
    },{
    	ref:'grille_resultats',
    	//selector:'evaluation_affichage #tab-resultats'
    	selector:'evaluation_affichage #grille_resultats'
    },{
    	ref:'general',
    	selector:'evaluation_affichage #tab-autres > #infos_eval_general'
    },{
    	ref:'detail',
    	selector:'evaluation_affichage #tab-autres > #infos_eval_detail'
    },{
    	ref:'btn_sauvegarder',
    	selector:'evaluation_resultats #btn_sauvegarder'
    }],
    
    stores:['Evaluations'],
    init: function() {
    	console.log('init res')
    	this.control({    		
    		'evaluation_resultats' : {
    			'edit':function() {console.info('edition')}
    		},
    		
    		'evaluation_resultats #btn_autosync': {
    			'toggle': function(b,pressed) {
    				this.getBtn_sauvegarder().setDisabled(pressed)    				
    			}
    		},
    		
    		'evaluation_resultats #btn_sauvegarder': {
    		
    			'enable': function(t) {
    				t.setTooltip('Sauvegarder toutes les données après édition.')},
    			'disable':function(t) {
    				t.setTooltip('La sauvegarde est automatique.')},
    		
    			'click':function() {console.log('click')
    				 recs=this.getGrille_resultats().getStore().queryBy(
    					function(e,i) {return e.dirty})
    				console.log(recs,this.getGrille_resultats().getStore().getUpdatedRecords(),this.getGrille_resultats().getStore().autoSync)
    				//recs.each(function(r){console.log(r.getChanges())})
    				//recs.each(function(r){console.log(r); r.cancelEdit()})
    				 }
    		}
    	})
    	
    },
    
});