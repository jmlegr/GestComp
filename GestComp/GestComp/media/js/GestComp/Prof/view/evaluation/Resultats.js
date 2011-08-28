Ext.define('GestComp.Prof.view.evaluation.Resultats',{	
	extend:'GestComp.ux.DynamicGrid',
	//store:'EvaluationResultats',
	alias:'widget.evaluation_resultats',
	modifColumn:function(column,columnRecue,index) {
		//console.log('colonne',column.dataIndex)
		if (column.dataIndex=="note") {
			//column.renderer=function(v){return 'pas de note'+v.note_max}
			//column.renderer=""
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
			pos=column.dataIndex.indexOf('_')
			champs='donnees'+column.dataIndex.substr(pos)
			//console.log('donnee',column.dataIndex,champs)
			column.xtype="templatecolumn";
			column.tpl=new Ext.XTemplate('<tpl><div data-qtip="{[this.remarques(values)]}">{[this.getClass(values)]}' +
                '<i data-qtip="{'+column.dataIndex+'}" class="{[this.getClass3(values)]}">{[this.score(values)]}</div></tpl>',
				{ 
				getClass: function(v) {
                	val=v[champs];
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
          			val=v[champs];
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
          			val=v[champs];
          			//console.log('score',val)
          			if (val.nb_faits==="0") return 'Non Fait';
          			st = (val.field?val.field:'--') + '</i>';
          			if (val.detail) return st+'/'+(val.nb_faits||val.items);
          			else return st;
  				},
  				remarques: function(v) {
          			val=v[champs];
          			return val.remarques?val.remarques:'aucune remarque'
  				}
				});
		}
		//return this.callParent(arguments)
		return column
	},
	modifStore:function(store,metaData) {
		
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
				record.commit()				
		})
		//console.log('store',store,metaData)
		return store
	}
})