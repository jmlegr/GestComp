Ext.define('GestComp.Prof.view.evaluation.Resultats',{	
	extend:'GestComp.ux.DynamicGrid2',
	//store:'EvaluationResultats',
	alias:'widget.evaluation_resultats',	
	initComponent :function() {
		//console.log(this.store)
		// override pour contourner bug EXTJSIV-2550, e.value n'est pas à jour
		Ext.grid.plugin.CellEditing.override({
			onEditComplete : function(ed, value, startValue) {
		        var me = this,
		            grid = me.grid,
		            sm = grid.getSelectionModel(),
		            activeColumn = me.getActiveColumn(),
		            dataIndex;
		        
		        if (activeColumn) {
		        	dataIndex = activeColumn.dataIndex;

		            me.setActiveEditor(null);
		            me.setActiveColumn(null);
		            me.setActiveRecord(null);
		            delete sm.wasEditing;
		    
		            //déplacé ici:
		            me.context.value = value;
		            
		            if (!me.validateEdit()) {
		                return;
		            }
		            // Only update the record if the new value is different than the
		            // startValue, when the view refreshes its el will gain focus
		            if (value !== startValue) {
		                me.context.record.set(dataIndex, value);
		            // Restore focus back to the view's element.
		            } else {
		                grid.getView().getEl(activeColumn).focus();
		            }
		            
		            // supprimé :
		            //me.context.value = value;
		            me.fireEvent('edit', me, me.context);
		        }
			}
		});
		
		var cellEditing = Ext.create('Ext.grid.plugin.CellEditing', {
	        clicksToEdit: 1
	    });
		var me=this;
		this.plugins=[cellEditing];
		this.dockedItems= [{
            xtype: 'toolbar',
            items: [{
                text: 'Editer',
                id:'btn_editer',
                iconCls: 'icon-pencil',
                tooltip:'Cliquer pour éditer',
                enableToggle: true,
                listeners: {
                          'toggle': {
                        	  fn :function(b,pressed) {
                        		  if (pressed) {
                        			  if (this.store.autoSync) b.setTooltip('Finir l\'édition.')
                        			  else b.setTooltip('Finir l\'édition.<p><b>Attention!</b>'+ 
                        					  ' cela n\'enregistre pas les données!')
                        		  } else b.setTooltip('Cliquer pour éditer.')
                        		  for (var i=0; i<this.headerCt.getColumnCount();i++) {
                        			  var ed=this.headerCt.getHeaderAtIndex(i).getEditor()
                        			  if (ed) {
                        				  if (pressed) ed.enable()			
                        				  else ed.disable()
                        			  }
                        		  }
                        	  	},
                        	  scope:this
                          }
                }
            /*
            }, '-', {
                text: 'Delete',
                iconCls: 'icon-delete',
                handler: function(){
                    var selection = grid.getView().getSelectionModel().getSelection()[0];
                    if (selection) {
                        store.remove(selection);
                    }
                }
            */
            }, '-', {
            	text: 'Sauvegarder',
            	id:'btn_sauvegarder',       	
                iconCls: 'icon-disk',
                disabled:true,
                tooltip:'La sauvegarde est automatique.'
                /*                
                listeners:{
                	'click': {
                		fn: this.onSave,
                			scope:this
                	}
                }
                */
            }]
		},{
			 weight: 2,
             xtype: 'toolbar',
             dock: 'bottom',
             items: [{
                 xtype: 'tbtext',
                 text: '<b>@cfg</b>'
             }, '|', {
            	 id:'btn_autosync',
                 text: 'Sauvegarde Auto',
                 enableToggle: true,
                 pressed: true,
                 tooltip: 'Si activé, les données sont sauvegardées automatiquement.',
                 scope: this,
                 toggleHandler: function(btn, pressed){
                     this.store.autoSync = pressed;
                 }
             /*
             }, {
                 text: 'batch',
                 enableToggle: true,
                 pressed: true,
                 tooltip: 'When enabled, Store will batch all records for each type of CRUD verb into a single Ajax request.',
                 scope: this,
                 toggleHandler: function(btn, pressed){
                     this.store.getProxy().batchActions = pressed;
                 }
             }, {
                 text: 'writeAllFields',
                 enableToggle: true,
                 pressed: false,
                 tooltip: 'When enabled, Writer will write *all* fields to the server -- not just those that changed.',
                 scope: this,
                 toggleHandler: function(btn, pressed){
                     this.store.getProxy().getWriter().writeAllFields = pressed;
                 }
             */
             }]
        }];
		
		this.callParent();
		this.on('validateedit',function(editor,e) {
			// PB: bug EXTJSIV-2550, e.value n'est pas à jour --> contourné par l'override ci-dessus
			this.onValidateedit(editor,e)
		})
		
		this.on('reconfigure',function(){
			//reset sur le bouton editer,sans relayer l'éevenement
			this.down('#btn_editer').toggle(false,true)
		});
		
	},
	onSync: function(){
		console.log('SYNCHRO')
        this.store.sync();
    },

    onDeleteClick: function(){
        var selection = this.getView().getSelectionModel().getSelection()[0];
        if (selection) {
            this.store.remove(selection);
        }
    },

    onAddClick: function(){
       
       
    },
	modifColumn:function(col,index) {
		column={}
		column=col
		//console.log('modifcolonne',index,column.dataIndex)
		if (column.dataIndex=="note") {
			//column.renderer=function(v){return 'pas de note'+v.note_max}
			//column.renderer=""
			column.width=40;
			column.tpl=new Ext.XTemplate('<tpl for="note">',	
											'<span style="{[values.incomplet?"color:red":""]}" ',
													'data-qtip="',
														'{[this.score(values)]} / {max}',
														'<p>{[values.incomplet?("<i style=&quot;color:red&quot;>incomplet (-"+values.non_remplis+")</i>"):',
														'"<i style=&quot;color:green&quot;>complet</i>"]}</p> ',
														'<p style=&quot;color:grey&quot;>Non faits:{non_faits}</p>',														
													'"',
													'>',
													
												'{[this.note(values)]}',
												'</span>',									 	
										 	'</tpl>',
										 	{
										 		compiled:true,
										 		score:function(v) {
										 			if (v.incomplet) sc='<span style=&quot;color:grey&quot;>'
										 			else sc='<span>'
										 			if (v.nota==null) sc+='--'
										 			else sc+=Ext.util.Format.number(v.nota,'0.00')
										 			if (v.bonus!=null) sc+=' + '+Ext.util.Format.number(v.bonus,'0.00')
										 			return sc+'</span>'
										 		},
										 		note:function(v){										 			
										 			if (v.resultat==null) sc='--'
										 			else sc=Ext.util.Format.number(v.resultat,'0.00')
										 			return sc
										 		}
										 	})
			column.xtype="templatecolumn"
		} else if (column.dataIndex.indexOf('resultat')!=-1) {
		//} else if (column.dataIndex.indexOf('donnees')!=-1) {
			var reg_d4="^(a\\+|a|na|ec\\+|ec\\-)";
			var reg_faits="(/([0-9]+(\\.?[0-9]+)?))?$";
			var reg_score="^(([0-9]+(\\.[0-9]+)?)(%)?)";
			var reg_nonfait="^(nf)$"
			var resultat_regexp=new RegExp(reg_nonfait +"|("+reg_d4+"|"+reg_score+")"+reg_faits,"i");		
			
			var pos=column.dataIndex.indexOf('_')
			var donnees='donnees'+column.dataIndex.substr(pos)
			var nb=column.nb_items
			//function de validation
			var validation=function(o) {
				tab=resultat_regexp.exec(o)
				// en 1:nf
				// en 3 : a ou na ou ec+ ou ec-
				// en 5 : valeur du score
				// en 7 : %
				// en 9 : valeur nb_faits
				var erreur=false
				if (tab) {
					if (tab[7]) {
						if (tab[5]>100) return 'Le purcentage ne peut être supérieur à 100'
						if (tab[9] && tab[9]>nb) return 'le nombre d\'items faits doit être \< '+nb 
					} else {
						if (tab[9]) {
							if (tab[9]>nb) return 'le nombre d\'items faits doit être \< '+nb 
							if (tab[5] && (tab[5]>tab[9])) return 'Le nombre d\'items doit être \< '+tab[9]
						}
						if (tab[5] && (tab[5]>nb)) return  'Le nombre d\'items doit être \< '+nb
					}
				}
				return true
			};
			
			column.editor= {
	                xtype: 'textfield',
	                allowBlank: false,
	                disabled:true,
	                maskRe:/[0-9/.%aecnf\+\-]/i, 
					regex: resultat_regexp,
					regexText: "Formes acceptées : 5.2 ou 5.2% ou 5.2/10 ou 5.2%/10, ou encore NA EC- EC+ A ou A+/10",
					selectOnFocus:true,
					validator:validation,
					ignoreNoChange:true,
	            }
			column.xtype="templatecolumn";
			var score=donnees+'.score', 
				items=donnees+'.items',
				nb_faits=donnees+'.nb_faits'
			column.tpl=new Ext.XTemplate('<tpl><div data-qtip="{[this.remarques(values)]}">{[this.getClass(values)]}' +
                '<i data-qtip="Score:{'+score+'}'+
                '<p>Items: {'+items+'}</p>'+
                '<p>Faits: {'+nb_faits+'}</p>" class="{[this.getClass3(values)]}">{[this.score(values)]}</div></tpl>',
				{ 
				getClass: function(v) {
                	val=v[donnees];
                	if (val.detail) {
                    	p=val.score/val.items;
                    	st= '<span class="imgdetail';
                    	if (p>=0.75) st+=' imgdetailA"></span></span>'
                    	else if (p>=0.50) st+=' imgdetailEC2"></span></span>'
                    	else if (p>=0.25) st+=' imgdetailEC1"></span></span>'
                    	else st+=' imgdetailNA"></span></span>'                    
                    }
                	else st= '</span>';
                	if (val.methode.toUpperCase()=="PO") return '<span height=14px class="testimg testimgPO">'+st
                	else if (val.methode.toUpperCase()=="PR") return '<span height=14px class="testimg testimgPR">'+st
                	else return '<span height=14px class="testimg testimgD4">'+st
                },  			
 				getClass3: function(v) {
          			val=v[donnees];
          			if (!val.field) {
          				//console.log('pas field');
          				return ""};
          			if (val.nb_faits==='0') return "cssNF";
          			if (val.detail) diviseur=val.nb_faits||val.items;
                    else diviseur=val.items;
          			p=val.score/diviseur;
          			if (p>=0.95) {return "cssAplus"};
          			if (p>=0.75) {return "cssA"};
          			if (p>=0.50) {return "cssEC2"};
          			if (p>=0.25) {return "cssEC1"};
          			if (p>=0) return "cssNA";
          			return ""
  				},
  				score: function(v) {
          			val=v[donnees];
          			//console.log('score',val)
          			if (val.nb_faits==="0") return 'Non Fait';
          			st = (val.field?val.field:'--') + '</i>';
          			if (val.detail) return st+'/'+(val.nb_faits||val.items);
          			else return st;
  				},
  				remarques: function(v) {
          			val=v[donnees];
          			return val.remarques?val.remarques:'aucune remarque'
  				}
				});
		}
		//return this.callParent(arguments)
		return column
	},
	modifStore:function(store,metaData) {
		//console.log('modifstore)')
		// calcul des notes
		store.each(function(record) {			
				var note_max=record.get('note').note_max
				var note=null 	
				var max=null
				var bonus=null
				var incomplet=false
				var non_faits=0
				var non_remplis=0
				//console.log('record',record)
				for (j=0;j<record.fields.keys.length;j++) {
					n=record.fields.keys[j];
					if (n.indexOf('donnees')==0){
						/*
						 *  il s'agit de données utilisables
						 *  on met à jour les notes (idem dans panlEvaluation majNote
						 *  TODO: unifier la fonction pour ces deux cas
						 */
						record_donnees=record.data[n]
						if (record_donnees.score==='') non_remplis+=1
						if (record_donnees.nb_faits=='0') non_faits+=1
						if (record_donnees.a_note) {	
							/*
							 * c'est noté, on compte suivant l'option
							 * '-' : obligatoire 
							 * 'O' : optionnel ; ne compte que si fait (ie nb_faits!=0)
							 * 'B' : bonus rajoute des points (relatifs)
							 * si l'utilisateur a entré une valeur de points c'est cette valeur
							 * qui est comptée - y compris en cas d'option non faite,
							 * sinon on prend les points_calcules
							 */
							if (record_donnees.option=='-') {
								max+=record_donnees.bareme*1
								if (record_donnees.points!="") {
									note+=record_donnees.points*1									
								} else if (record_donnees.points_calcules!="") {
									note+=record_donnees.points_calcules*1
								} else incomplet=true
							} else if (record_donnees.option=="O") {
								if (record_donnees.points!="") {
									max+=record_donnees.bareme*1
									note+=record_donnees.points*1									
								} else if (record_donnees.points_calcules!="" && record_donnees.nb_faits!="0") {
									max+=record_donnees.bareme*1
									note+=record_donnees.points_calcules*1
								}
							} else {
								// c'est un bonus
								if (record_donnees.points!="") {
									bonus+=record_donnees.points*1
								} else bonus+=record_donnees.points_calcules*1
							}
							
						}					
					}				
				}
				//console.log(i,note,max,bonus,records[i].data)
				//records[i].data.note=note+"/"+max+bonus?("+"+bonus):""+incomplet?"(inc)":"(comp)"
				resultatString=note+"/"+max
				if (bonus!=null) {
					resultatString+=' +'+bonus
					resultat=(note+bonus)/max*note_max
				}
				else if (max!=null) resultat=(note/max)*note_max
				resultatString+=incomplet?"(inc)":"(complete)"
				record.data.note={}
				record.data.note.texte=resultatString
				record.data.note.nota=note
				record.data.note.incomplet=incomplet
				record.data.note.bonus=bonus
				record.data.note.max=max
				record.data.note.note_max=note_max
				record.data.note.non_faits=non_faits
				record.data.note.non_remplis=non_remplis
				//records[i].data.note.resultat=(note!=null)?(Math.round(note*20*100/max)/100):null
				record.data.note.resultat=(note!=null)?(note*note_max/max).toFixed(2):null
						//console.log(record.data.note)
				record.commit()				
		})
		//console.log('store',store,metaData)
		return store
	},
	onValidateedit: function(editor,e) {
		// TODO: sortir directement lorsqu'il n'y a pas d'edition en cours
		//met a jour les différents champs de donnees suivant ce qui a été entré (ex 2%/10 ou EC+/20)						
		
		donnees='donnees'+e.field.substring(e.field.indexOf('_'))
		resultat='resultat'+e.field.substring(e.field.indexOf('_'))
		//console.log('validate edit',e,e.field,e.record.get(e.field),e.value);
		//for (var i in e) {console.log(i,' >> ',e[i])}
		rec_copie=e.record.get(donnees)
		// on fait une copie pour que le changement soit bien noté (isModified() )
		// note : ne fonctionne que pour une copie simple, sans objets ni methodes
		var rec=new Object()
		for (var i in rec_copie) rec[i]=rec_copie[i]
		
		// on filtre avec la regexp
		var reg_d4="^(a\\+|a|na|ec\\+|ec\\-)";
		var reg_faits="(/([0-9]+(\\.?[0-9]+)?))?$";
		var reg_score="^(([0-9]+(\\.[0-9]+)?)(%)?)";
		var reg_nonfait="^(nf)$"
		var resultat_regexp=new RegExp(reg_nonfait +"|("+reg_d4+"|"+reg_score+")"+reg_faits,"i");
		//tab=resultat_regexp.exec(e.record.get(e.field))
		tab=resultat_regexp.exec(e.value)
		// en 1:nf
		// en 3 : a ou na ou ec+ ou ec-
		// en 5 : valeur du score
		// en 7 : %
		// en 9 : valeur nb_faits
		if (tab != null) {
			rec.methode=(tab[3]?"d4":(tab[7]?"Po":"Pr"))
			if (tab[9]) {rec.nb_faits=tab[9]}
			else if (!tab[1]) {rec.nb_faits=(rec.nb_faits!=0)?rec.nb_faits:rec.items
			}
			if (tab[3]) {
				acquis=tab[3].toUpperCase();
				field=acquis
				rec.field=field
				switch (acquis) {
					// on calcule le score
					case 'A+' :
						rec.score=1*(rec.detail?rec.nb_faits:rec.items)
						break;
					case 'A' : 
						rec.score=.94*(rec.detail?rec.nb_faits:rec.items)
						break
					case 'NA':
						rec.score=.24
						break
					case 'EC+':
						rec.score=.74*(rec.detail?rec.nb_faits:rec.items)
						break
					case 'EC-':
						rec.score=.49*(rec.detail?rec.nb_faits:rec.items)
						break
				}
			}
			else if (tab[7]) {
				// on calcule le score : du pourcentage au score
				if (rec.detail) {if (rec.nb_faits=='') rec.nb_faits=rec.items}
				field=tab[5]+'%'
				rec.score=tab[5]*(rec.detail?rec.nb_faits:rec.items)/100.0
				rec.field=tab[5]+'%'								
			}
			else if (tab[1]) {
				rec.score="0"
				rec.nb_faits='0'
				field='NF'
				rec.field=field
			}
			else {
				rec.score=tab[5];
				field=rec.score
				rec.field=field
			}
			
		} else {
			field=''
			rec.score=""
			rec.nb_faits=rec.items
			rec.field=field
		}
		field+='/'+rec.nb_faits	
		bareme=rec.bareme?rec.bareme:rec.items
		if (rec.score=='') rec.points_calcules=''
		else {
			if (rec.detail && rec.nb_faits!=0) {
				rec.points_calcules=""+rec.score*rec.bareme/rec.nb_faits
			} else {
				rec.points_calcules=""+rec.score*rec.bareme/rec.items
			}	
		}
		// on compare la valeur initiale de resultat_ à celle calculée après edit
		different=(e.record.get(resultat)!==field)
		if (different) {						
			// on sauvegarde resultat 
			// et on annule les évènements suivant l'update de resultat_
			e.record.data[resultat]=field
			// si on est en autoSync, on ne marque pas le dirty
			if (this.store.autoSync) e.cancel=true
			// on marque les modifications dans donnees_
			e.record.set(donnees,rec)
		} else {
			//console.log('reject');
			e.cancel=true
		}
		 
	},
	sauvegarder: function() {
		var store=this.store,	
			me=this,
			modified = this.store.getUpdatedRecords(),
			eval=this.eval;
		
		if (modified.length > 0) {
			var recordsToSend = [];			
			Ext.each(modified, function(record) {
				recordsToSend.push(record.getChanges());
				//recordsToSend.push(record.data.eleve_id) //: pas nécessaire, on a l'id de la compétence_evaluée
			});
			
			var el=this.el
			el.mask('sauvegarde...',"x-mask-loading")
			Ext.Ajax.request({ 				
				url: 'evaluations/modif_resultats', 
				jsonData: {data: recordsToSend},
				success : function(result,response) { 
					el.unmask();
					json=Ext.decode(result.responseText)
					if (json.success) {
						Ext.each(modified, function(record) {record.commit()})
						//GestComp.Bus.fireEvent('message','Gestion Evaluation',json.msg)
					}
					else {
						r='<div style="padding-left:3em;">';						
						for (msg in json.errorMessage) {
							r+='<li><i>'+msg+'</i>::' +json.errorMessage[msg]+'</li>'
						}
						r+='</div>'
						//GestComp.Bus.fireEvent('erreur','Gestion Eval: ERREUR',r,true)
						Ext.Msg.alert('Erreur',r)
						me.reload(eval.id)
					}
					
					 
				} 
			}); 
		}
		
	},
})