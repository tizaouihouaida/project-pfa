INSERT INTO Utilisateurs_utilisateur VALUES(1,'pbkdf2_sha256$870000$JsPd9zfz1nUtepFBKV560Y$SuJouPwKSSDNEKJ8n+wNPnA6GzUFP1ezALKtZTz+4dw=','2025-01-07 18:26:57.864180',0,'golden','','','golden@gmail.com',0,1,'2025-01-03 18:36:49.556405','gestionnaire_stocks','957458663');
INSERT INTO Utilisateurs_utilisateur VALUES(2,'pbkdf2_sha256$870000$bbrSCOXX6CqkRWerg7ysaJ$4MRa+QSK9AyPCF1cFPCz0NtEO8i8NRqb5jc/dkogJHQ=','2025-01-07 18:27:58.050794',0,'jean','','','jean@gmail.com',0,1,'2025-01-04 00:08:45.719339','gestionnaire_ventes','78965241');
INSERT INTO GestionStocks_categoriemedicament VALUES(1,'Analgésiques','Médicaments contre la douleur.',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(2,'Antibiotiques','Médicaments pour traiter les infections bactériennes.',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(3,'Antihistaminiques','Médicaments contre les allergies',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(4,'Anti-inflammatoires','Médicaments pour réduire l''inflammation',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(5,'Antidiarrhéiques','Médicaments contre la diarrhée',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(6,'Antiacides','Médicaments pour soulager les brûlures d''estomac',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(7,'Antihypertenseurs','Médicaments pour traiter l''hypertension',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(8,'Antidiabétiques','Médicaments pour traiter le diabète',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(9,'Antidépresseurs','Médicaments pour traiter la dépression',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(10,'Anxiolytiques','Médicaments pour traiter l''anxiété',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(11,'Anticoagulants','Médicaments pour prévenir les caillots sanguin',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(12,'Antifongiques','Médicaments pour traiter les infections fongiques',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(13,'Antiviraux','Médicaments pour traiter les infections virales',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(14,'Vitamines et suppléments','Compléments alimentaires (vitamine C, vitamine D).',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(15,'Produits dermatologiques','Crèmes et lotions pour la peau (hydrocortisone, émollients).',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(16,'Produits pour les soins oculaires','Gouttes pour les yeux, solutions de rinçage (collyre, sérum physiologique).',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(17,'Produits pour les soins buccaux','Bains de bouche, dentifrices spécialisés (chlorhexidine, fluor).',0);
INSERT INTO GestionStocks_categoriemedicament VALUES(18,'Contraceptifs','Médicaments et dispositifs contraceptifs (pilule contraceptive, préservatifs).',1);
INSERT INTO GestionStocks_categoriemedicament VALUES(19,'Produits pour la santé des femmes','Tampons, serviettes hygiéniques, traitements pour les infections vaginales.',1);
INSERT INTO GestionStocks_medicament (id_Medicament, nom, description, prixUnitaire, image, est_vendu, est_cachee, id_Categorie_id) VALUES
(1, 'DOLIPRANE 1000 mg', 'Traitement de la douleur et fièvre', 500.00, 'medicament_images/DOLIPRANE_1000_mg.jpg', true, false, 1),
(2, 'EFFERALGAN', 'Soulage rapidement douleurs légères', 700.00, 'medicament_images/Efferalgan_500_mg.jpg', true, false, 1),
(3, 'IBUPROFENE Biogramm 200 mg', 'Réduit douleurs et inflammation', 600.00, 'medicament_images/Ibuprofène_Biogaran_200_mg.jpg', true, false, 4),
(4, 'IBUPROFENE Biogramm 400 mg', 'Réduit douleurs et inflammation', 450.00, 'medicament_images/IBUPROFENE_Biogramm_400_mg.jpg', true, false, 1),
(5, 'ASPIRINE 100 mg', 'Antalgique et anti-inflammatoire', 600.00, 'medicament_images/aspirine_100_mg.jpg', true, false, 1),
(6, 'AMOXICILLINE 500 mg', 'Antibiotique à large spectre • Traite infections bactériennes', 1200.00, 'medicament_images/amoxicilline_500_mg.jpg', true, false, 2),
(7, 'AUGMENTIN 500 125 mg', 'Combinaison amoxicilline/acide clavulanique • Efficace contre infections résistantes', 2500.00, 'medicament_images/augmentin_500_125_mg.jpg', true, false, 2),
(8, 'AUGMENTIN Sirop', 'Combinaison amoxicilline/acide clavulanique • Efficace contre infections résistantes', 2150.00, 'medicament_images/augmentin_sirop_KdLB3b3.jpg', true, false, 2),
(9, 'CIPROFLOXACINE 500 mg', 'Antibiotique fluoroquinolone • Traite infections urinaires/digestives', 1800.00, 'medicament_images/ciprofloxacine_500_mg.jpg', true, false, 2),
(10, 'CIPROFLOXACINE 750 mg', 'Antibiotique fluoroquinolone • Traite infections urinaires/digestives.', 2125.00, 'medicament_images/ciprofloxacine_750_mg.jpg', true, false, 2),
(11, 'ZYRTEC 10 mg', 'Traite allergies respiratoires', 1500.00, 'medicament_images/Zyrtec_10_mg.png', true, false, 3),
(12, 'CLARITYNE 10 mg', 'Soulage symptômes allergiques', 1200.00, 'medicament_images/clarityne_10_mg.jpg', true, false, 3),
(13, 'AERIUS', 'Anti-allergique nouvelle génération', 1800.00, 'medicament_images/aerius_5_mg.jpg', true, false, 3),
(14, 'AERIUS Sirop', 'Anti-allergique nouvelle génération', 1950.00, 'medicament_images/aerius_sirop.jpg', true, false, 3),
(15, 'RHINADVIL', 'Traite rhinites allergiques', 1000.00, 'medicament_images/RHINADVIL_Rhume.jpg', true, false, 3),
(16, 'PROFENID', 'Soulage douleurs articulaires', 1500.00, 'medicament_images/profenid_100_mg.jpg', true, false, 4),
(17, 'VOLTARENE 75mg', 'Traite rhumatismes et tendinites', 1200.00, 'medicament_images/voltarene_75_mg.jpg', true, false, 4),
(18, 'VOLTARENE Emulgel', 'Traite rhumatismes et tendinites', 1350.00, 'medicament_images/voltarene_emulgel.jpg', true, false, 4),
(19, 'ASPEGIC 100mg', 'Anti-inflammatoire classique', 600.00, 'medicament_images/aspegic_100_mg.jpg', true, false, 4),
(20, 'ASPEGIC 100 mg Nourrisson', 'Anti-inflammatoire classique chez les nourrissons', 500.00, 'medicament_images/aspegic_nourrisson_100_mg.jpg', true, false, 4);

INSERT INTO GestionStocks_fournisseur VALUES(1,'kodjo betsaleel sessou','sessoukodjogolden@gmail.com','92367425','Amoutivé, lom-nava');