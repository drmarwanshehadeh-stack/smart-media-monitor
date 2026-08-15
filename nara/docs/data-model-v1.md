# NARA Data Model v1

## منهجية عامة

المشروع بحثي وتحليلي. كل الأرقام العملياتية المستخرجة من صحيفة النبأ تسجل افتراضياً بوصفها `claimed`، أي ادعاءات المصدر، ولا تُعامل كوقائع مؤكدة ما لم توجد طبقة تحقق مستقلة.

## 1. issues
سجل العدد نفسه.

حقول مقترحة:
- issue_number
- issue_date_hijri
- issue_date_gregorian
- pages
- source_file_id_or_ref
- canonical_copy
- ingestion_status
- notes

## 2. weekly_claims
يمثل بيانات صفحة «حصاد الأجناد» أو أي إنفوغراف أسبوعي مجمع.

حقول مقترحة:
- issue_number
- reporting_period_start
- reporting_period_end
- claimed_operations_total
- claimed_killed_wounded_total
- claimed_damaged_disabled_vehicles
- claimed_sites_burned
- claimed_houses_burned
- claimed_captives
- claimed_by_province_json
- source_page
- verification_status = claimed
- extraction_confidence

قاعدة: لا تجمع أرقام الإنفوغراف مع الأحداث التفصيلية لإنتاج مجموع جديد. الإنفوغراف يستخدم كـ aggregate مرجعي للمطابقة.

## 3. events
صف واحد لكل حدث عملياتي معلن بعد إزالة التكرار.

حقول أساسية:
- event_id
- issue_number
- source_page
- event_date
- claimed_province
- normalized_country
- admin_area
- locality
- event_type
- target_type
- target_name
- claimed_killed
- claimed_wounded
- claimed_captured
- claimed_vehicles_destroyed
- claimed_vehicles_damaged
- claimed_sites_burned
- claimed_houses_burned
- weapons_or_method
- source_section
- claim_status
- corroboration_sources
- dedupe_key
- extraction_confidence

## 4. editorials
سجل لكل افتتاحية.

حقول أساسية:
- issue_number
- title
- main_idea
- communication_topic_primary
- communication_topic_secondary
- ideological_reference_types
- ideological_reference_functions
- main_actors
- primary_communication_goal
- secondary_communication_goals
- primary_frame
- secondary_frame
- self_other_structure
- enemy_category
- legitimacy_mechanism
- violence_legitimation_0_4
- mobilization_0_4
- emotional_register
- temporal_orientation
- geographic_orientation
- position_on_state_borders_governance
- change_topic
- change_enemy
- change_frame
- change_mobilization
- change_violence_legitimation
- operations_discourse_alignment
- analyst_note
- coding_confidence

## 5. verification
طبقة منفصلة للتحقق الخارجي ولا تغير الادعاء الأصلي.

قيم الحالة:
- claimed: ورد في المصدر فقط
- corroborated: تأكد وقوع الحدث من مصدر مستقل، مع احتمال اختلاف التفاصيل
- verified: دعمته عدة مصادر مستقلة موثوقة بدرجة عالية
- disputed: توجد أدلة مستقلة تناقض الادعاء أو بعض عناصره
- unresolved: لا تكفي البيانات للحكم

## قواعد منع العد المزدوج
1. الخبر التفصيلي + حصاد الأجناد = سجل حدث واحد، لا عمليتان.
2. فقرة «الأسبوع الماضي» لا تدخل في الفترة الحالية إذا سبق تسجيلها.
3. إعادة سرد العملية نفسها في تقرير أو تعليق لا ينشئ حدثاً جديداً.
4. الحدث المتعدد المراحل يُعامل كحدث واحد إذا قدمه المصدر كسياق عملياتي واحد متصل؛ وإلا يفصل وفق التاريخ والمكان والهدف.
5. لا تُستكمل قيمة مفقودة من الإنفوغراف اعتماداً على التخمين.

## المخرجات الزمنية
- Weekly: العدد الواحد
- Monthly: تجميع الأحداث بعد إزالة التكرار، مع إبقاء aggregates الأصلية للمطابقة
- Quarterly: اتجاهات ومعدلات تغير
- Annual: الاتجاه الجغرافي والعملياتي والخطابي طويل المدى
