Ext.define('GestComp.grid.Competences',{
	requires:['GestComp.stores.competences'],
	//alias:'widget.grideleves',
	extend:'Ext.tree.Panel',
	title:'Grille Compétences(défaut)',
	
	initComponent: function(){
		Ext.apply(this, {
           //store:[new GestComp.stores.competences.CompetenceTree],
			//store:{xtype:'tt'},
			rootVisible: false,
			
		   columns:[
				{header:'id',dataIndex:'id',hidden:true},
				{header:'Nom',dataIndex:'nom',xtype:'treecolumn',flex:1},
				{header:'description',dataIndex:'description',hidden:true},
				{header:'test',dataIndex:'user',hidden:true},
				{header:'créé par',dataIndex:'user',hidden:true,
				xtype:'templatecolumn',align:'center',
				tpl:Ext.create('Ext.XTemplate','{user:this.test}', {
					test: function(v) {
					 if (v===null) return 'aucun'
					 if (v==user.id) {return 'moi'} else {return v}}
				})
				}
			],
			
			 listeners:{
			 'add':function(s,r,i) {console.log('append',r,i)},
			 'load':function(t,n,r){
			 	NODE=t
			 	console.log(t)
			 }
			 /*
        	'load':function(t,n,r) {
        		
        		tt=t;nn=n;rr=r
        		console.log(t.getUpdatedRecords())
        		//n.getUI().addClass('cssNA')
        		n.eachChild(function(){
        			console.info('child',this.data.is_root)
        			if (this.data.is_root) {  console.info('cls',this)      						
        				//this.data.setCls('cssGras')
        				this.data.cls='cssGras'
        				if (this.data.niveau!=null) {
        				//if (this.attributes.niveau!=null) { 
        					//this.setText(this.attributes.nom)
        					this.setTooltip(this.data.qtip+'<p><b>Niveau: '+this.data.niveau+'</b></p>')
        					//this.setTooltip(this.attributes.qtip+'<p><b>Niveau: '+this.attributes.niveau+'</b></p>')
        				} else {
        					//this.setText(this.attributes.nom)
        				}
        				//this.setCls('node-Critical-severity')
        			} else {
        				if (this.data.liens) {
        				//if (this.attributes.liens) {
        					//this.setText(this.attributes.nom)
        					this.setTooltip(this.data.qtip+'<p>('+this.data.liens+' liens)</p>')
        					//this.setTooltip(this.attributes.qtip+'<p>('+this.attributes.liens+' liens)</p>')
        					//this.setTooltip(this.attributes.qtip+'<p><i>('+this.attributes.liens+' liens )</i></p>'))
        				} else {
        					//this.setText(this.attributes.nom)
        				}
        				
        			}
        		})
        	}*/
        } 
        
     	 });
		me=this;
		this.store=new GestComp.stores.competences.CompetenceTree
 		this.callParent(arguments);
 		        
 		this.getView().on('render', function(view) {
    		view.tip = Ext.create('Ext.tip.ToolTip', {
        // 		The overall target element.
        		target: view.el,
        // 		Each grid row causes its own seperate show and hide.
        		delegate: view.itemSelector,
        // 		Moving within the row should not hide the tip.
        		trackMouse: true,
        		// ne disparait que lorsque qu'on sort de la cible
        		dismissDelay:0,
        		showDelay:2000,
        // 		Render immediately so that tip.body can be referenced prior to the first show.
        		renderTo: Ext.getBody(),
        		
        		/*
        		 * premiere méthode: avec tpl et les données en json : renderer:'data'
        		 * (pas de reader definissable(?) donc envois direct des données JSON coté serveur {nom:'truc',prenom:'bidule'}
        		 * ou rajouter <tpl for="root"> si on renvoie dans root (ici >tpl for="data">)
        		 * ou bien passer par la méthode "success" et décoder
        		 * 
        		 * deuxième méthode: retour dirct en html: renderer:'html' (defaut)
        		 * côté serveur sous django : 
        		 * 	resp=HttpResponse()
        		 *  resp.write('<p>truc</p>')
        		 *  resp.write('<i>bidue</i>')
        		 *  return resp
        		 */
        		tpl:Ext.create('Ext.XTemplate',
        			'<tpl for="data">'+
        			' <p>liens:<tpl>{nbliens}</tpl></p>'+
        			' <tpl for="liens">'+
        			'  <p><tpl if="xindex==1"><b><i>Origine:</i></b></tpl>'+
        			'     <tpl if="xindex != 1">{# - 1}:</tpl>'+
        			'(Graphe N°{graphe})</p>'+
        			'  <ul>'+
        			'  <tpl for="liste">'+
        			' 	<li> {[this.espaces(xindex)]}'+
        			'        <tpl if="type_lien"> !! </tpl>'+
        			'        <tpl if="depth==1"><b></tpl>{type_lien} {nom} ({utilisateur})'+
        			'        <tpl if="depth==1"></b></tpl></li>'+
        			'  </tpl>'+
        			'  </ul>'+
        			' </tpl>'+
        			'</tpl>',{
        			espaces:function(n){
        					s=''
        					for (i=1;i<=n;i++) {s+='.'}
        					return s
        				}        			
        		}),
        		
        		loader: {
        			url: '/competences/infos_competence',
        			loadMask:true,
        			renderer: 'data',        			
        			params: {
            			userId: 1            		
        			},        			
    			},

    			listeners: {
            // Change content dynamically depending on which element triggered the show.
            		beforeshow: function updateTipBody(tip) {            			
            			record=view.getRecord(tip.triggerElement);  
            			//tip.update('<b>Infos sur <i>'+record.get('nom')+'</i></b>');
            			//tip.setTitle('Infos sur <i>'+record.get('nom')+'</i>');
            			this.getLoader().load({params:{id:record.data.id}})
            		}
            		
        		}
    	});
 		});
		/*
		this.on({afterlayout:{scope:this, single:true, fn:function() {
							console.log('tot',me.store)
							me.store.load({params:{start:0}})
			}}
        });
        */
	}
});