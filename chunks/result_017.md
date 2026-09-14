1. Domain model (mô hình miền) và hạ tầng messaging (truyền tin nhắn) của bạn dùng chung một persistence store (kho lưu trữ dữ liệu bền vững, chẳng hạn như cùng một data source). Cách tiếp cận này cho phép các thay đổi trên mô hình và thao tác ghi nhận tin nhắn mới được commit trong cùng một local transaction (giao dịch cục bộ). Ưu điểm của nó là hiệu năng tương đối tốt. Nhược điểm tiềm ẩn là các vùng lưu trữ của hệ thống tin nhắn (như các bảng cơ sở dữ liệu) phải nằm trong cùng một cơ sở dữ liệu (hoặc schema) với mô hình của bạn — điều này tùy thuộc vào gu thiết kế của từng đội ngũ. Dĩ nhiên, đây sẽ không phải là một lựa chọn khả thi nếu kho lưu trữ của mô hình và kho lưu trữ của cơ chế tin nhắn không thể chia sẻ chung với nhau.
2. Persistence store của domain model và persistence store của hệ thống tin nhắn được kiểm soát dưới một global transaction chuẩn XA (giao dịch phân tán với cơ chế two-phase commit — cam kết hai pha). Ưu điểm ở đây là bạn có thể tách rời hoàn toàn nơi lưu trữ mô hình và nơi lưu trữ tin nhắn. Tuy nhiên, nhược điểm là các global transaction đòi hỏi sự hỗ trợ chuyên biệt từ hệ thống, điều mà không phải persistence store hay hệ thống tin nhắn nào cũng đáp ứng được. Các global transaction thường gây tốn kém tài nguyên và có hiệu năng kém. Ngoài ra, cũng có khả năng kho lưu trữ của mô hình hoặc kho lưu trữ của cơ chế tin nhắn (hoặc cả hai) không tương thích với chuẩn XA.
3. Bạn tạo một vùng lưu trữ đặc biệt (ví dụ: một bảng cơ sở dữ liệu) dành cho các Event (sự kiện) trong cùng persistence store được dùng để lưu trữ domain model. Đây chính là một Event Store (kho lưu trữ sự kiện), như sẽ được thảo luận kỹ hơn ở phần sau của chương này. Cách này tương tự như phương án 1; tuy nhiên, vùng lưu trữ này không do cơ chế truyền tin nhắn sở hữu và kiểm soát, mà thuộc quyền quản lý của chính Bounded Context (ngữ cảnh giới hạn) của bạn. Một thành phần out-of-band (ngoài luồng xử lý chính) do bạn tự tạo sẽ đọc Event Store để xuất bản (publish) toàn bộ các Event đã lưu nhưng chưa được gửi qua cơ chế tin nhắn. Ưu điểm ở đây là mô hình và các Event của bạn được đảm bảo tính nhất quán tuyệt đối trong phạm vi một local transaction duy nhất. Nó còn mang lại các lợi ích đặc trưng khác của Event Store, bao gồm khả năng cung cấp các REST-based notification feed (luồng cấp phát thông báo dựa trên REST). Cách tiếp cận này cho phép sử dụng một hạ tầng tin nhắn có kho lưu trữ tin nhắn hoàn toàn riêng biệt. Tuy vậy, do cơ chế tin nhắn trung gian (middleware) chỉ được kích hoạt sau khi Event đã được lưu trữ, nhược điểm của giải pháp này là bạn phải tự phát triển bộ chuyển tiếp Event (Event forwarder) để đẩy dữ liệu qua hệ thống tin nhắn, đồng thời các client (phía nhận) bắt buộc phải được thiết kế để có khả năng de-duplicate (khử trùng lặp tin nhắn) khi nhận (xem mục 'Event Store').

Trong các ví dụ của mình, tôi sử dụng cách tiếp cận thứ ba. Mặc dù vẫn có những nhược điểm nhất định, giải pháp này mang lại nhiều ưu điểm vượt trội sẽ được làm rõ trong mục 'Event Store'. Việc tôi lựa chọn hướng tiếp cận này hoàn toàn không phủ nhận giá trị của những đánh đổi (trade-offs) khác. Bạn và đội ngũ của mình cần cân nhắc để đưa ra lựa chọn phù hợp nhất giữa các phương án.

## Autonomous Services and Systems

Việc sử dụng Domain Events (sự kiện miền) cho phép xây dựng bất kỳ hệ thống doanh nghiệp nào theo định hướng autonomous services and systems (các dịch vụ và hệ thống tự trị). Tôi sử dụng thuật ngữ *autonomous service* (dịch vụ tự trị) để đại diện cho bất kỳ dịch vụ nghiệp vụ mức hạt thô (coarse-grained business service) nào — có thể xem như một hệ thống hoặc một ứng dụng — vận hành phần lớn độc lập với các "dịch vụ" khác trong doanh nghiệp. Dịch vụ tự trị có thể sở hữu nhiều endpoint giao diện dịch vụ, nghĩa là nó cung cấp nhiều giao diện dịch vụ kỹ thuật cho các remote client. Mức độ độc lập cao đối với các hệ thống khác đạt được nhờ việc loại bỏ hoàn toàn các lệnh gọi thủ tục từ xa nội luồng (in-band RPC - Remote Procedure Call), nơi mà một yêu cầu từ người dùng chỉ được xem là hoàn tất khi yêu cầu gọi API sang một hệ thống từ xa thành công.

Vì sẽ có những thời điểm hệ thống từ xa bị gián đoạn hoàn toàn hoặc rơi vào trạng thái quá tải, RPC có thể trực tiếp đe dọa đến khả năng thành công của hệ thống phụ thuộc. Rủi ro này sẽ nhân lên theo cấp số nhân khi số lượng hệ thống tích hợp qua RPC API mà nó phụ thuộc gia tăng. Do đó, việc tránh sử dụng in-band RPC giúp giải tỏa đáng kể sự phụ thuộc cũng như hạn chế các sự cố sập toàn diện hoặc suy giảm hiệu năng nghiêm trọng bắt nguồn từ các hệ thống từ xa chậm chạp hoặc không khả dụng.

Thay vì gọi trực tiếp sang các hệ thống khác, hãy sử dụng cơ chế truyền tin nhắn bất đồng bộ (asynchronous messaging) để đạt được tính tự trị và mức độ độc lập cao hơn giữa các hệ thống. Khi nhận được tin nhắn mang theo Domain Event từ các Bounded Context khác trong doanh nghiệp, hãy kích hoạt hành vi nghiệp vụ trên chính mô hình của bạn sao cho phản ánh đúng ý nghĩa của các Event đó trong phạm vi Bounded Context của mình. Điều này không đồng nghĩa với việc bạn chỉ đơn giản là sao chép dữ liệu (replicate data) hay tạo ra các bản sao y hệt của các đối tượng từ dịch vụ khác vào dịch vụ của mình. Đúng là một số dữ liệu có thể được sao chép giữa các hệ thống — tối thiểu sẽ bao gồm định danh duy nhất (unique identity) của các Aggregate (cụm thực thể / cốt lõi nghiệp vụ) bên ngoài. Nhưng các đối tượng ở hệ thống này hiếm khi, hoặc gần như không bao giờ, là bản sao nguyên xi của các đối tượng từ các hệ thống lân cận. Nếu sai lầm mô hình hóa này xảy ra, hãy tham khảo chương Bounded Contexts (2) và Context Maps (3) để hiểu lý do vì sao nó có hại và cách khắc phục. Trên thực tế, nếu Domain Event được thiết kế chuẩn xác, chúng rất hiếm khi mang toàn bộ đối tượng như một phần trạng thái của mình.

Event sẽ chỉ chứa một lượng giới hạn các tham số lệnh và/hoặc trạng thái của Aggregate đủ để truyền tải ý nghĩa nghiệp vụ, giúp các Bounded Context đăng ký nhận tin có thể phản ứng chính xác. Dĩ nhiên, nếu một Event không cung cấp đủ thông tin cho một bên nhận cụ thể, bản hợp đồng (contract) trên toàn domain của Event đó sẽ phải được điều chỉnh để cung cấp những dữ liệu cần thiết. Điều này thường đồng nghĩa với việc phải thiết kế một phiên bản mới tường minh cho Event hoặc tạo ra một Event hoàn toàn khác.

Cũng phải thừa nhận rằng trong một số trường hợp, việc sử dụng RPC rất khó tránh khỏi. Một số hệ thống di sản (legacy system) chỉ có khả năng cung cấp giao tiếp qua RPC. Thêm vào đó, khi việc chuyển ngữ một khái niệm hoặc một nhóm khái niệm từ Bounded Context bên ngoài về Bounded Context nội bộ quá phức tạp, việc suy luận ngữ nghĩa đầy đủ từ nhiều Event có thể làm tăng độ phức tạp của hệ thống. Nếu bạn buộc phải tái tạo gần như toàn bộ các khái niệm, đối tượng và mối quan hệ của mô hình bên ngoài vào mô hình của mình, bạn có thể phải cân nhắc tiếp tục dùng RPC. Điều này cần được xem xét trên từng trường hợp cụ thể, và lời khuyên của tôi là không nên nhượng bộ chuyển sang dùng RPC quá dễ dàng. Nếu thực sự bất khả kháng, bạn có thể chấp nhận dùng RPC hoặc cố gắng tác động để đội ngũ sở hữu mô hình bên ngoài tìm cách đơn giản hóa thiết kế của họ — dù phải thừa nhận rằng việc tác động này rất khó, nếu không muốn nói là bất khả thi.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000328_08b8c915925784180a89c4959f27fc2b3954d9ca09e505ce56bc87548f36505d.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000329_e1beadadedd0b2806e35313ce293664cf6fe08a97c8c262bea7804e7144780f5.png)

## Latency Tolerances

Liệu những khoảng thời gian trễ tiềm ẩn trước khi nhận được tin nhắn — khi mà tính nhất quán sau cùng (eventual consistency) gây ra độ trễ lớn hơn vài mili-giây — có gây ra vấn đề không? Chắc chắn đây là một khía cạnh cần được cân nhắc kỹ lưỡng, bởi dữ liệu không đồng bộ có thể dẫn đến những hành động sai sót, thậm chí gây thiệt hại. Chúng ta phải tự hỏi: khoảng thời gian trễ giữa các trạng thái nhất quán bao lâu là chấp nhận được, và mức trễ bao nhiêu thì vượt quá giới hạn? Các chuyên gia miền (domain expert) thường nắm rất rõ đâu là độ trễ chấp nhận được và đâu là không. Các lập trình viên có thể sẽ ngạc nhiên khi biết rằng trong phần lớn trường hợp, độ trễ vài giây, vài phút, vài giờ, hay thậm chí vài ngày giữa các trạng thái nhất quán là hoàn toàn có thể dung thứ được. Điều này không có nghĩa là nó luôn đúng cho mọi tình huống. Nhưng chúng ta không được mặc định cho rằng trong bất kỳ domain nào, việc đạt được trạng thái nhất quán tức thì cũng là yêu cầu bắt buộc.

Đôi khi, câu hỏi sau sẽ mở ra một câu trả lời mang nhiều giá trị thông tin: Trước khi có máy tính thì nghiệp vụ vận hành như thế nào, hoặc nếu bây giờ không có máy tính thì nó sẽ chạy ra sao? Có lẽ ngay cả hệ thống vận hành trên giấy tờ đơn giản nhất cũng không bao giờ đạt được tính nhất quán tức thì. Do đó, việc các hệ thống máy tính tự động hóa có thể chấp nhận, thậm chí vận hành hiệu quả dựa trên mô hình nhất quán sau cùng, là điều hoàn toàn hợp lý. Chúng ta có thể kết luận rằng tính nhất quán sau cùng mang lại ý nghĩa kinh doanh thực tế hơn.

Hãy tưởng tượng một Subdomain (miền con) được dùng để lập kế hoạch cho các hoạt động tương lai của đội ngũ. Khi bất kỳ hoạt động riêng lẻ nào được phê duyệt, một Domain Event phản ánh sự phê duyệt đó sẽ được xuất bản: `TeamActivityApproved`. Event này tiếp nối hàng loạt các Event khác đã được xuất bản trước đó về sự hình thành và định nghĩa của các hoạt động nay đã được duyệt. Một Bounded Context khác phản ứng với việc phê duyệt này bằng cách lên lịch cho hoạt động vừa sẵn sàng bắt đầu vào một thời điểm thích hợp tương quan với tất cả các hoạt động đã được phê duyệt khác.

Chúng ta biết rằng bất kỳ hoạt động nào cũng được lên kế hoạch và phê duyệt trước khi diễn ra ít nhất vài tuần. Đã như vậy thì liệu việc Event dùng để đưa hoạt động đã duyệt vào lịch trình đến trễ vài phút, vài giờ, hay thậm chí vài ngày sau khi phê duyệt có thực sự thành vấn đề không? Có thể vài ngày là không ổn. Tuy nhiên, nếu một sự cố sập hệ thống khiến Event bị trễ vài tiếng đồng hồ — một tình huống hiếm khi xảy ra — thì việc thiếu hoạt động đó trên lịch trong vài giờ có phải là độ trễ hoàn toàn không thể chấp nhận được không? Không hề, bởi vì sự cố hệ thống hy hữu này là điều hoàn toàn có thể khắc phục được, và dù sao thì hoạt động đó cũng phải vài tuần nữa mới bắt đầu. Do đó, một độ trễ điển hình khoảng vài giây — ở mức tối đa — để Event được gửi đến trong điều kiện vận hành bình thường không những có thể dung thứ được, mà còn hoàn toàn chấp nhận được. Trên thực tế, người dùng thậm chí còn không nhận ra được độ trễ đó.

## Cowboy Logic

AJ: "Đó là 'chút xíu' kiểu Kentucky à?"

LB: "Có khi lại là một 'phút' kiểu New York đấy."

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000330_cbf05381213c364c959251bd074d4e9eda5d2c4db79b96a4a876d2ac0b674fdb.png)

> 💡 **Giải thích thêm:** Tác giả dùng phép ẩn dụ mang tính văn hóa Mỹ để nói về mức độ chịu trễ (latency tolerance) trong tính nhất quán sau cùng (eventual consistency):
> - *"Kentucky shortly"* ám chỉ lối sống thư thái miền quê ở bang Kentucky, nơi người ta bảo "sắp xong rồi / chờ một lát" nhưng có thể là vài giờ hoặc cả ngày sau.
> - *"New York minute"* là thành ngữ chỉ nhịp sống hối hả tại New York, nơi "một phút" diễn ra chớp nhoáng trong tích tắc (vài phần giây).
> Đoạn đối thoại nhấn mạnh rằng: trong nghiệp vụ thực tế, "nhất quán sau cùng" không nhất thiết phải nhanh như chớp mắt (New York minute), mà đôi khi hoàn toàn có thể thong thả kéo dài vài giờ hay vài ngày (Kentucky shortly) mà vẫn đáp ứng hoàn hảo yêu cầu bài toán.
> Nguồn tham khảo: [Wiktionary: New York minute](https://en.wiktionary.org/wiki/New_York_minute)

Dù ví dụ trên là hoàn toàn thực tế, các dịch vụ nghiệp vụ khác vẫn có thể đòi hỏi thông lượng (throughput) cao hơn nhiều. Mức chịu trễ tối đa cần phải được thấu hiểu rõ ràng, và các hệ thống phải sở hữu các đặc tính kiến trúc đủ để đáp ứng, thậm chí vượt trên các tiêu chuẩn đó. Tính sẵn sàng cao (high availability) và khả năng mở rộng (scalability) phải được thiết kế ngay từ đầu vào các dịch vụ tự trị cùng hạ tầng truyền tin nhắn hỗ trợ để đáp ứng chuẩn xác các phi chức năng (nonfunctional requirements) khắt khe của doanh nghiệp.

## Event Store

Việc duy trì một kho lưu trữ chứa toàn bộ các Domain Event cho một Bounded Context đơn lẻ đem lại nhiều lợi ích tiềm năng. Hãy thử hình dung bạn có thể làm được những gì nếu lưu lại từng Event riêng biệt cho mọi hành vi lệnh (command) từng được thực thi trên mô hình. Bạn có thể:

1. Sử dụng Event Store như một hàng đợi (queue) để xuất bản tất cả các Domain Event thông qua một hạ tầng tin nhắn. Đây là một trong những mục đích sử dụng chính trong cuốn sách này. Nó cho phép tích hợp giữa các Bounded Context, nơi các remote subscriber (bên nhận từ xa) phản ứng với các Event dựa theo nhu cầu ngữ cảnh của riêng họ. (Xem mục trước, 'Spreading the News to Remote Bounded Contexts.')
2. Sử dụng chính Event Store đó để cấp phát các thông báo Event dưới dạng REST cho các client truy vấn dạng kéo (polling). (Về mặt logic, điều này tương tự như điểm 1, nhưng khác biệt trong cách thức sử dụng thực tế.)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000331_fdc7fc2aa2ba77af09f25784dc6b5a226a478ff9ce57653413d22e467f3dbb03.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000332_d3bb7fecf152999942e1358363396c9ba2bc29b85ebbadf2784b1a094570c750.png)

3. Kiểm tra bản ghi lịch sử kết quả của mọi lệnh từng được thực thi trên mô hình. Điều này hỗ trợ truy vết lỗi (bug), không chỉ trong mô hình mà còn ở phía client. Cần nắm rõ rằng Event Store không đơn thuần là một bản log kiểm toán (audit log). Nhật ký kiểm toán có thể hữu ích cho việc gỡ lỗi, nhưng chúng hiếm khi ghi lại đầy đủ toàn bộ kết quả sau mỗi lệnh của Aggregate.
4. Sử dụng dữ liệu phục vụ việc phân tích xu hướng, dự báo và các nghiệp vụ phân tích kinh doanh (business analytics) khác. Nhiều khi doanh nghiệp không biết cách tận dụng nguồn dữ liệu lịch sử này cho đến khi nhận ra họ thực sự cần nó trong tương lai. Trừ khi Event Store được duy trì ngay từ đầu, dữ liệu lịch sử sẽ không có sẵn khi nhu cầu phát sinh.
5. Sử dụng các Event để tái lập (reconstitute) trạng thái của từng phiên bản Aggregate khi nó được truy xuất từ Repository (kho chứa thực thể). Đây là phần bắt buộc trong kiến trúc Event Sourcing (mô hình lưu trữ trạng thái dựa trên chuỗi sự kiện). Kỹ thuật này được thực hiện bằng cách áp dụng tuần tự toàn bộ các Event đã lưu trữ trước đó lên một thể hiện Aggregate theo đúng thứ tự thời gian. Bạn có thể tạo snapshot (bản chụp trạng thái) sau một số lượng Event nhất định (chẳng hạn mỗi cụm 100 Event) để tối ưu hóa tốc độ tái lập đối tượng.
6. Dựa trên ứng dụng của điểm số 5, bạn có thể hoàn tác (undo) các khối thay đổi trên Aggregate. Điều này khả thi bằng cách ngăn chặn (có thể thông qua việc xóa bỏ hoặc đánh dấu là lỗi thời) một số Event nhất định không được áp dụng khi tái lập thể hiện Aggregate. Bạn cũng có thể vá (patch) Event hoặc chèn thêm Event để sửa lỗi trong luồng sự kiện (event stream).

Tùy thuộc vào mục đích xây dựng Event Store, nó sẽ mang các đặc tính tương ứng. Vì các ví dụ trong tài liệu này chủ yếu hướng đến lợi ích 1 và 2, Event Store của chúng ta về cơ bản chỉ tập trung vào việc lưu trữ các Event đã được tuần tự hóa (serialized) theo đúng thứ tự phát sinh. Điều này không có nghĩa là chúng ta không thể dùng các Event này để hiện thực hóa toàn bộ 4 lợi ích đầu tiên, bởi vì hai lợi ích tiếp theo hoàn toàn khả thi khi chúng ta đã ghi lại toàn bộ các sự kiện quan trọng trong miền nghiệp vụ. Do đó, đạt được lợi ích 3 và 4 chính là ứng dụng mở rộng từ những gì đã thực hiện ở hai mục đầu. Tuy nhiên, chúng ta sẽ không đi sâu vào việc khai thác Event Store cho điểm 5 và 6 trong chương này.

Cần thực hiện một số bước để hiện thực hóa lợi ích 1 và 2. Các bước này được tóm tắt trong Hình 8.3. Trước tiên, hãy thảo luận về các bước trong biểu đồ tuần tự (sequence diagram) đó cùng các thành phần liên quan thông qua trải nghiệm thực tế từ dự án SaaSOvation.

Bất kể lý do sử dụng Event Store là gì, một trong những việc đầu tiên cần làm là tạo ra một subscriber (bên lắng nghe) để tiếp nhận mọi Event được xuất bản từ mô hình. Đội ngũ phát triển quyết định thực hiện việc đó bằng cách dùng một hook hướng khía cạnh (AOP - Aspect-Oriented Programming) có khả năng can thiệp vào luồng thực thi của mọi Application Service (dịch vụ tầng ứng dụng) trong hệ thống.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000333_1fa9ca6e441a84417735e9c456c8f8c88b0d1974cdb14dfbfa0153f2bb981e13.png)

Hình 8.3 `IdentityAccessEventProcessor` đăng ký nhận tin nặc danh cho tất cả các Event của mô hình. Nó ủy quyền cho `EventStore`, nơi sẽ tuần tự hóa từng Event thành một `StoredEvent` và lưu trữ lại.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000334_6806d50d6126a5a2c98328d72e91252d6a18e113e3bf8702ea19f4eea87f7745.png)

Dưới đây là cách đội ngũ SaaSOvation triển khai cho `Identity and Access Context`. Thành phần sau mang trách nhiệm duy nhất là đảm bảo tất cả các Domain Event đều được lưu trữ:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000335_6e0df3093024052db014127944a0dc8353ba82ecc3c41f0a5418c4b363cd95fe.png)

```java
@Aspect
public class IdentityAccessEventProcessor {
    ...
    @Before("execution(* com.saasovation.identityaccess.application.*.*(..))")
    public void listen() {
        DomainEventPublisher
            .instance()
            .subscribe(new DomainEventSubscriber<DomainEvent>() {
                public void handleEvent(DomainEvent aDomainEvent) {
                    store(aDomainEvent);
                }

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000336_2a5863dde76eb74ff5b080a78784e0d80ecff971d94e23593d204c83dd4b7c81.png)

```java
                public Class<DomainEvent> subscribedToEventType() {
                    return DomainEvent.class; // tất cả các domain event
                }
            });
    }

    private void store(DomainEvent aDomainEvent) {
        EventStore.instance().append(aDomainEvent);
    }
}

```

Đây là một bộ xử lý Event đơn giản, và bất kỳ Bounded Context nào khác có cùng nhiệm vụ đều có thể áp dụng cách tương tự. Nó được thiết kế dưới dạng một aspect (sử dụng Spring AOP) để chặn (intercept) tất cả các lời gọi phương thức của Application Service. Khi một phương thức của Application Service được thực thi, bộ xử lý này sẽ thiết lập để lắng nghe toàn bộ các Domain Event được xuất bản từ các tương tác giữa Application Service với mô hình. Bộ xử lý đăng ký một subscriber với thể hiện `DomainEventPublisher` gắn liền theo thread (thread-bound). Bộ lọc của subscriber này mở hoàn toàn, thể hiện qua việc phương thức `subscribedToEventType()` trả về `DomainEvent.class`. Việc trả về lớp này đồng nghĩa với việc subscriber muốn nhận tất cả các Event. Khi `handleEvent()` được gọi, nó ủy quyền cho `store()`, và hàm này tiếp tục ủy thác cho lớp `EventStore` để thêm Event vào cuối Event Store thực tế.

Dưới đây là phương thức `append()` của thành phần `EventStore`:

```java
package com.saasovation.identityaccess.application.eventStore;
...
public class EventStore ... {
    ...
    public void append(DomainEvent aDomainEvent) {
        String eventSerialization =
            EventStore.objectSerializer().serialize(aDomainEvent);

        StoredEvent storedEvent = new StoredEvent(
            aDomainEvent.getClass().getName(),
            aDomainEvent.occurredOn(),
            eventSerialization);

        this.session().save(storedEvent);
        this.setStoredEvent(storedEvent);
    }
}

```

Phương thức `store()` thực hiện tuần tự hóa thể hiện `DomainEvent`, đóng gói nó vào một thể hiện `StoredEvent` mới, rồi ghi đối tượng mới này vào Event Store. Dưới đây là một phần của lớp `StoredEvent` dùng để lưu trữ `DomainEvent` đã tuần tự hóa:

```java
package com.saasovation.identityaccess.application.eventStore;
...
public class StoredEvent {
    private String eventBody;
    private long eventId;
    private Date occurredOn;
    private String typeName;

    public StoredEvent(
        String aTypeName,
        Date anOccurredOn,
        String anEventBody) {

        this();
        this.setEventBody(anEventBody);
        this.setOccurredOn(anOccurredOn);
        this.setTypeName(aTypeName);
    }
    ...
}

```

Mỗi thể hiện `StoredEvent` nhận một giá trị chuỗi tuần tự duy nhất được tự động sinh bởi cơ sở dữ liệu và được gán vào `eventId`. Thuộc tính `eventBody` chứa chuỗi tuần tự hóa của `DomainEvent`. Chuỗi tuần tự hóa ở đây sử dụng định dạng JSON thông qua thư viện [Gson], nhưng chúng ta hoàn toàn có thể dùng định dạng khác. `typeName` giữ tên lớp cụ thể của `DomainEvent` tương ứng, và `occurredOn` là bản sao thời gian từ thuộc tính `occurredOn` trong `DomainEvent`.

Tất cả các đối tượng `StoredEvent` được lưu vào một bảng MySQL. Dung lượng lưu trữ được thiết lập rất rộng rãi cho chuỗi tuần tự hóa của Event, dù 65.000 ký tự chắc chắn vượt xa dung lượng mà một thể hiện đơn lẻ có thể cần tới:

```sql
CREATE TABLE `tbl_stored_event` (
    `event_id` int(11) NOT NULL auto_increment,
    `event_body` varchar(65000) NOT NULL,
    `occurred_on` datetime NOT NULL,
    `type_name` varchar(100) NOT NULL,
    PRIMARY KEY (`event_id`)
) ENGINE=InnoDB;

```

Phần trên đã điểm qua ở mức tổng quan một số thành phần cần thiết để xây dựng Event Store chứa toàn bộ các thể hiện Event được xuất bản bởi các Aggregate trong domain model. Chúng ta sẽ tìm hiểu chi tiết hơn sau. Tiếp theo, hãy xem cách các hệ thống khác có thể tiêu thụ (consume) những bản ghi đã lưu trữ về các sự kiện phát sinh trong mô hình.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000337_fd774d9e54e26b34cc9f08a2dc240ad58c08fa55498f7d5d8161445258ce8ea5.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000338_e7d5ab1d8c0eaa081a679490c77bfd86519b134dea22d54f59718b6fefe6d8d1.png)

## Architectural Styles for Forwarding Stored Events

Một khi Event Store đã được đổ dữ liệu, nó sẵn sàng cung cấp các Event để chuyển tiếp dưới dạng thông báo đến các bên quan tâm. Chúng ta sẽ xem xét hai phong cách kiến trúc để phân phối các Event này. Một phong cách là thông qua các tài nguyên RESTful được client truy vấn, và phong cách thứ hai là gửi tin nhắn qua một topic/exchange của một sản phẩm phần mềm truyền tin nhắn trung gian (messaging middleware).

Phải thừa nhận rằng cách tiếp cận dựa trên REST không hẳn là một kỹ thuật chuyển tiếp (forwarding) thuần túy. Tuy nhiên, nó được sử dụng để đạt được kết quả tương tự như phong cách Xuất bản - Đăng ký (Publish-Subscribe), tương tự cách một e-mail client đóng vai trò là "subscriber" tiếp nhận các thông điệp e-mail được "publish" bởi một máy chủ e-mail.

## Publishing Notifications as RESTful Resources

Phong cách thông báo Event qua REST hoạt động hiệu quả nhất trong môi trường tuân theo các nguyên lý cơ bản của Publish-Subscribe. Nghĩa là, có nhiều consumer cùng quan tâm đến các event phát sinh từ một producer duy nhất. Ngược lại, nếu bạn cố gắng sử dụng phong cách dựa trên REST như một Hàng đợi (Queue), phương pháp này sẽ bộc lộ nhiều hạn chế. Dưới đây là tổng kết mặt ưu và khuyết của giải pháp RESTful:

* Nếu nhiều client có thể cùng truy cập vào một URI định danh duy nhất để yêu cầu cùng một tập hợp thông báo, giải pháp RESTful hoạt động rất tốt. Về bản chất, các thông báo được phân phối đồng loạt (fanned out) tới nhiều consumer thực hiện polling. Điều này tuân theo đúng mẫu hình Publish-Subscribe cơ bản, dù nó dùng mô hình kéo (pull model) thay vì mô hình đẩy (push model). 2
* Nếu một hoặc một vài consumer buộc phải kéo tài nguyên từ nhiều producer khác nhau nhằm thực thi một chuỗi tác vụ theo thứ tự cụ thể, bạn sẽ nhanh chóng thấy được sự bất cập của phương pháp RESTful. Tình huống này mô tả một Hàng đợi (Queue), nơi nhiều producer cần đẩy thông báo vào cho một hoặc một vài consumer xử lý, và thứ tự tiếp nhận có thể mang tính quyết định. Mô hình polling thường không phải là lựa chọn thích hợp để triển khai Hàng đợi.

2. Xem http://c2.com/cgi/wiki?ObserverPattern để tìm hiểu thảo luận về mô hình push và pull khi kết hợp với mẫu hình Observer.

Cách tiếp cận RESTful để xuất bản các thông báo Event hoàn toàn trái ngược với cách xuất bản thông qua một hạ tầng tin nhắn thông thường. Phía "publisher" không duy trì danh sách các "subscriber" đã đăng ký vì không có dữ liệu nào được chủ động đẩy (push) đến các bên quan tâm. Thay vào đó, cách này yêu cầu các REST client phải chủ động kéo (pull) thông báo thông qua một URI xác định.

Hãy xem xét phương pháp RESTful từ góc nhìn tổng quan. Nếu bạn đã quen thuộc với cách các Atom feed hoạt động trên Web, cách tiếp cận này sẽ rất quen mắt. Trên thực tế, nó được xây dựng dựa trên các khái niệm của Atom.

Các client sử dụng phương thức HTTP GET để yêu cầu tài nguyên được gọi là current log (nhật ký hiện hành). Current log chứa các thông báo mới nhất vừa được xuất bản. Phía client nhận được current log với số lượng thông báo không vượt quá giới hạn định sẵn. Trong ví dụ của chúng ta, số lượng thông báo tối đa cho mỗi log là 20. Client sẽ duyệt qua từng Event trong current log để tìm ra tất cả các sự kiện mà Bounded Context của nó chưa tiêu thụ.

Làm thế nào để một client tiêu thụ các thông báo Event tại nội bộ? Nó diễn giải Event đã tuần tự hóa theo loại (type), chuyển đổi mọi dữ liệu thích hợp sang ngữ cảnh của Bounded Context nội bộ. Quá trình này thường bao gồm việc định vị các thể hiện Aggregate liên quan trong mô hình của chính nó và thực thi các lệnh dựa trên kết quả giải mã các Event thích hợp. Dĩ nhiên, các Event bắt buộc phải được áp dụng theo đúng thứ tự thời gian, bởi các Event cũ nhất đại diện cho các thao tác đã diễn ra trước các sự kiện mới hơn. Trừ khi các Event cũ nhất được áp dụng trước theo đúng thứ tự phát sinh, những thay đổi tác động lên mô hình nội bộ rất có thể sẽ dẫn đến lỗi logic.

Trong quá trình triển khai của chúng ta, current log sẽ chứa tối đa 19 thông báo. Nó có thể chứa ít hơn 19, thậm chí bằng 0. Khi current log đạt tổng cộng 20 thông báo, nó sẽ tự động được lưu trữ (archived). Nếu không có thông báo mới nào phát sinh tại thời điểm current log trước đó vừa được lưu trữ, current log mới sẽ hoàn toàn trống rỗng.

## What's an Archived Log All About?

Không có gì bí ẩn về một archived log (nhật ký lưu trữ). Nó chỉ đơn giản là bản log đó không còn bị thay đổi bởi bất kỳ hành động nào trong hệ thống sở hữu, và client được đảm bảo rằng dù họ có yêu cầu một archived log cụ thể bao nhiêu lần đi nữa, nội dung của nó sẽ luôn luôn bất biến.

Ngược lại, current log sẽ liên tục thay đổi cho đến khi đầy và chính thức được lưu trữ thành archived log. Tuy nhiên, thay đổi duy nhất có thể diễn ra đối với current log chỉ là việc ghi nhận thêm các thông báo mới cho đến khi nó đạt mức giới hạn.

Các Event đã được thêm vào bất kỳ log nào trước đó tuyệt đối không bao giờ được phép thay đổi. Điều này là bắt buộc vì client cần một sự đảm bảo rằng một khi họ đã áp dụng một Event cụ thể tại nội bộ, sự kiện đó đã được xử lý duy nhất một lần và dứt điểm cho mọi thời điểm về sau.

Do đó, current log không phải lúc nào cũng chứa thông báo mới nhất hoặc cũ nhất chưa được áp dụng ở phía client. Event cũ nhất như vậy có thể đang nằm ở bản log ngay trước current log, hoặc thậm chí ở các log trước đó nữa. Tất cả phụ thuộc vào tần suất các Event lấp đầy một bản log hữu hạn (trong trường hợp này chỉ có 20 mục) và tần suất client thực hiện thao tác pull log. Hình 8.4 minh họa cách các notification log liên kết với nhau tạo thành một mảng ảo chứa các thông báo riêng lẻ.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000339_d6abd2126edead0c2f781e0a59df2b3563361f86e244ff54bb286b2d03d4f44b.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000340_bd583a708dd74f2ab9df9c66fcf31410b0143070a52ee5cb0667e03dfe47c4cf.png)

Giả định trạng thái log như mô tả trong Hình 8.4, giả sử các thông báo từ 1 đến 58 đã được xử lý cục bộ. Điều này đồng nghĩa các thông báo từ 59 đến 65 vẫn chưa được áp dụng. Nếu client thực hiện pull từ URI sau, nó sẽ nhận được current log:

//iam/notifications

Client đọc từ cơ sở dữ liệu của chính mình bản ghi theo dõi định danh của thông báo được áp dụng gần đây nhất, trong ví dụ này là 58. Trách nhiệm theo dõi thông báo tiếp theo cần xử lý thuộc về client chứ không phải server. Client duyệt từ trên xuống dưới trong current log để tìm thông báo mang định danh 58. Khi không tìm thấy, nó tiếp tục điều hướng ngược về log trước đó — vốn là một archived log. Log trước đó được truy cập thông qua một liên kết hypermedia nằm trong current log. Một phong cách thường dùng là cho phép điều hướng hypermedia thông qua header:

```http
HTTP/1.1 200 OK
Content-Type: application/vnd.saasovation.idovation+json
...
Link: <http://iam/notifications/61,80>; rel=self
Link: <http://iam/notifications/41,60>; rel=previous
...

```

Hình 8.4 Current log cùng với một chuỗi các archived log được liên kết tạo thành một mảng ảo chứa tất cả các Event từ Event gần nhất ngược về Event đầu tiên. Ở đây thể hiện các thông báo từ 1 đến 65. Mỗi archived log chứa đủ giới hạn 20 thông báo. Current log hiện chưa đầy và mới chỉ chứa tổng cộng 5 thông báo.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000341_1a2bbeb1c918cdcb46b2b1433f76ee694d125ae8464a64d0821ee5078229054c.png)

## Why Doesn't the URI Reflect What's Actually in the Current Log?

Lưu ý rằng mặc dù current log hiện chỉ chứa các thông báo mang định danh từ 61 đến 65, URI của nó vẫn được tạo thành từ toàn bộ dải định danh đầy đủ, từ 61 đến 80, ví dụ:

```http
Link: <http://iam/notifications/61,80>; rel=self

```

Lý do là tài nguyên phải giữ được tính ổn định trong suốt vòng đời của nó. Điều này đảm bảo việc truy cập luôn nhất quán và cơ chế caching (lưu bộ nhớ tạm) hoạt động chuẩn xác.

Từ liên kết `Link` chứa `rel=previous`, URI đó được dùng cho một yêu cầu `GET` nhằm lấy về bản log đứng ngay trước current log:

```
//iam/notifications/41,60

```

Truy xuất vào archived log này, lúc này client tìm thấy thông báo cần tìm mang định danh 58 sau ba lần kiểm tra trên từng thông báo riêng lẻ (60, 59, rồi đến 58). Vì client này đã xử lý thông báo đó (định danh 58) rồi, nó sẽ không áp dụng lại thông báo 58 nữa. Thay vào đó, nó chuyển hướng điều hướng theo chiều ngược lại để tìm kiếm tất cả các thông báo mới hơn. Trong archived log này, nó tìm thấy định danh 59 và áp dụng nó. Tiếp theo, nó tìm thấy 60 và áp dụng tiếp. Đến đây nó đã đi tới đỉnh của archived log này, vì vậy nó điều hướng sang tài nguyên `rel=next`, chính là current log:

```http
HTTP/1.1 200 OK
Content-Type: application/vnd.saasovation.idovation+json
...
Link: <http://iam/notifications/61,80>; rel=next
Link: <http://iam/notifications/41,60>; rel=self
Link: <http://iam/notifications/21,40>; rel=previous
...

```

Trong log này, client tìm thấy các thông báo mang định danh 61, 62, 63, 64 và 65, rồi lần lượt xử lý từng thông báo theo đúng thứ tự thời gian. Khi chạm đến phần cuối của current log, nó tạm dừng quá trình xử lý, bởi vì current log không bao giờ chứa header liên kết dạng `rel=next`.

Một thời gian sau, quy trình này lặp lại. Current log lại được yêu cầu qua URI. Có thể lúc này hoạt động trong Bounded Context nguồn đã tạo ra các bản log mới đáng kể bằng việc sinh thêm nhiều thông báo mới. Khi current log được yêu cầu ở thời điểm này, nó có thể mang thêm nhiều thông báo mới. Phía client có thể phải duyệt ngược lại một, hai hoặc thậm chí nhiều archived log hơn để định vị được thông báo đã xử lý gần nhất — hiện tại là thông báo mang định danh 65. Tương tự như trước, khi client tìm thấy thông báo 65, nó sẽ áp dụng tất cả các thông báo mới hơn theo thứ tự thời gian.

Bất kỳ Bounded Context client nào cũng có thể yêu cầu các notification log này. Trên thực tế, bất kỳ Bounded Context nào cần nắm bắt các Event được sinh ra bởi một Bounded Context khác có cung cấp cơ chế xuất bản thông báo này đều có thể vươn tới để lấy thông báo ngược về tận "thuở ban đầu". Dĩ nhiên, mỗi Bounded Context chỉ có thể thực sự đóng vai trò client nếu nó có quyền truy cập hợp lệ vào hệ thống nguồn (chẳng hạn như quyền bảo mật).

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000342_45a7a6759c225e1a95ffcbe069167b869523d1435b78f9322c5877d9ceb49533.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000343_677019af49e7a09a047ac8578ee7795d31a21c13bc1edc42746155088e06f5f2.png)

Nhưng liệu việc client liên tục polling các tài nguyên thông báo có tạo ra lượng truy cập khổng lồ ngoài ý muốn lên máy chủ Web của bạn hay không? Sẽ không thành vấn đề nếu các tài nguyên RESTful của bạn tận dụng hiệu quả cơ chế caching. Ví dụ, current log có thể được cache ngay tại chính client trong khoảng thời gian khoảng một phút:

```http
HTTP/1.1 200 OK
Content-Type: application/vnd.saasovation.idovation+json
...
Cache-Control: max-age=60
...

```

Mỗi lần client thực hiện polling trước khi hết thời hạn một phút của cache, chính bộ nhớ cache của client sẽ trả về current log đã nhận trước đó. Khi cache hết hạn, current log mới nhất sẽ được kéo về từ tài nguyên trên server. Các archived log có thể được cache lâu hơn vì nội dung của chúng không bao giờ thay đổi, minh chứng qua giá trị `max-age` dài một giờ này:

```http
HTTP/1.1 200 OK
Content-Type: application/vnd.saasovation.idovation+json
...
Cache-Control: max-age=3600
...

```

Phía client có thể sử dụng giá trị `max-age` của current log như một ngưỡng hẹn giờ/ngủ (timer/sleep threshold), giúp tránh việc phải liên tục thực hiện các yêu cầu `GET` lên các tài nguyên đã được cache. Việc giảm tần suất polling thông qua trạng thái sleep giúp giải tỏa tải xử lý cho cả Bounded Context của client lẫn server nguồn. Phía cung cấp tài nguyên sẽ không bao giờ phải tiếp nhận các yêu cầu đó chừng nào `max-age` của cache chưa hết hạn. Vì vậy, một client xử lý kém chuẩn mực cũng không thể làm tổn hại đến hiệu năng hoặc tính sẵn sàng của producer phát thông báo, với điều kiện client đó áp dụng cơ chế cache đúng cách. Điều này làm nổi bật những lợi ích to lớn của việc tận dụng nền tảng Web cùng cơ sở hạ tầng có sẵn để đạt được hiệu năng và khả năng mở rộng vượt trội.

Server cũng có thể tự trang bị bộ nhớ cache riêng. Việc server cache các notification log hoạt động cực kỳ hiệu quả vì nội dung của các archived log là bất biến. Bất kỳ client nào yêu cầu một archived notification log nhất định không chỉ nhận được tài nguyên đó, mà còn đồng thời làm ấm (warm) cache cho tất cả các client khác có cùng nhu cầu. Server cache hoàn toàn không cần phải làm mới (refresh) một archived log vì tính bất biến của nó đã được đảm bảo tuyệt đối.

Thật tuyệt vời! Chúng ta vừa đi qua một khối lượng chi tiết đáng kể, và vẫn còn nhiều điều thú vị khác nằm trong chương Integrating Bounded Contexts (13). Tôi khuyến khích bạn tham khảo tài liệu [Parastatidis et al., RiP] để nắm bắt các chiến lược thiết kế hệ thống thông báo Event qua REST hiệu quả. Tại đó, bạn sẽ tìm thấy các phân tích về ưu và nhược điểm của các notification log dựa trên chuẩn media type Atom, cùng một số implementation (hiện thực hóa) tham khảo. Ngoài ra, Jim Webber cũng cung cấp thêm nhiều góc nhìn sâu sắc về phương pháp này trong bài thuyết trình [Webber, REST & DDD]. Một trong những tài liệu sớm nhất đề cập đến giải pháp này đến từ bài viết của Stefan Tilkov trên InfoQ [Tilkov, RESTful Doubts]. Bạn cũng có thể xem bài thuyết trình của chính tôi về việc áp dụng giải pháp này [Vernon, RESTful DDD].

## Publishing Notifications through Messaging Middleware

Không có gì đáng ngạc nhiên khi một sản phẩm messaging middleware như RabbitMQ có thể quản lý thay bạn những chi tiết phức tạp mà phong cách REST buộc bạn phải tự xử lý. Hệ thống tin nhắn cũng cho phép bạn hỗ trợ cả hai mô hình Publish-Subscribe và Hàng đợi (Queue) một cách khá dễ dàng, tùy thuộc vào mô hình nào đáp ứng tốt hơn nhu cầu của bạn. Trong cả hai trường hợp, hệ thống tin nhắn đều sử dụng mô hình đẩy (push model) để phân phối các thông báo Event đến các subscriber hoặc listener đã đăng ký.

Hãy xem xét các yêu cầu đối với việc xuất bản các Event từ Event Store của chúng ta thông qua một sản phẩm messaging middleware. Chúng ta sẽ kiên định với mô hình Publish-Subscribe, sử dụng cấu trúc mà RabbitMQ gọi là fanout exchange (bộ định tuyến phát sóng tới tất cả hàng đợi). Chúng ta sẽ cần một tập hợp các thành phần cùng phối hợp thực hiện tuần tự các bước sau:

1. Truy vấn tất cả các đối tượng Domain Event từ Event Store mà chưa được xuất bản tới exchange cụ thể đó. Sắp xếp các đối tượng truy vấn được theo thứ tự tăng dần dựa trên định danh duy nhất có tính tuần tự của chúng.
2. Lặp qua các đối tượng được truy vấn theo thứ tự tăng dần, gửi từng đối tượng tới exchange.
3. Khi hệ thống tin nhắn phản hồi rằng tin nhắn đã được xuất bản thành công, đánh dấu Domain Event đó là đã được xuất bản qua exchange tương ứng.

Chúng ta không cần chờ đợi xem các subscriber đã xác nhận việc nhận tin hay chưa. Thậm chí các hệ thống subscriber có thể còn chưa khởi chạy khi publisher gửi tin nhắn qua exchange. Mỗi subscriber chịu trách nhiệm xử lý các tin nhắn theo khung thời gian riêng của mình, đảm bảo thực thi đúng các hành vi nghiệp vụ cần thiết trên mô hình của chính nó. Chúng ta chỉ đơn giản dựa vào cơ chế tin nhắn để đảm bảo việc phân phối (delivery guarantee).

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000344_201a334dfc9bcf73afeab8ebee83d9632585da4ec0d673dd2e65c9274c75d786.png)

## Whiteboard Time

* Hãy vẽ một Context Map (bản đồ ngữ cảnh) thể hiện Bounded Context bạn đang phụ trách cùng các Context khác mà bạn đang tích hợp cùng. Hãy đảm bảo thể hiện rõ các kết nối giữa những Context có tương tác với nhau.
* Hãy ghi chú rõ các loại quan hệ giữa chúng, chẳng hạn như Anticorruption Layer (Lớp chống suy thoái) (3).
* Bây giờ hãy chỉ ra cách bạn sẽ tích hợp các Context này. Bạn sẽ dùng RPC, thông báo qua RESTful hay hạ tầng messaging? Hãy vẽ các phương án đó vào bảng.

Hãy nhớ rằng, bạn có thể không có nhiều sự lựa chọn khi phải tích hợp với một hệ thống di sản (legacy system).

## Implementation

Sau khi đã thống nhất về các phong cách kiến trúc dùng để xuất bản Event, đội ngũ SaaSOvation giờ đây tập trung vào việc hiện thực hóa các thành phần để hiện thực điều đó...

Cốt lõi của hành vi xuất bản thông báo được đặt sau một Application Service: `NotificationService`. Thiết kế này cho phép đội ngũ quản lý phạm vi giao dịch (transactional scope) của các thay đổi trong chính nguồn dữ liệu của mình. Nó cũng nhấn mạnh rằng việc thông báo là một mối bận tâm thuộc tầng ứng dụng (application concern), không phải của tầng nghiệp vụ (domain concern), mặc dù các Event được xuất bản dưới dạng thông báo vốn bắt nguồn từ chính domain model.

Ở thời điểm này, `NotificationService` chưa cần phải áp dụng mô hình Separated Interface (tách rời giao diện) [Fowler, P of EAA]. Hiện tại chỉ có duy nhất một implementation của

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000345_25eeb2f3bcc849c5a062a042b9b327c4265bbee51692928e20020a03d06ad6aa.png)

Application Service, vì vậy cả đội giữ cho mọi thứ thật đơn giản. Dù vậy, mọi lớp học cơ bản đều sở hữu một giao diện public, và dưới đây là khung phương thức (stubbed-out methods) ban đầu:

```java
package com.saasovation.identityaccess.application;
...
public class NotificationService {
    ...
    @Transactional(readOnly = true)
    public NotificationLog currentNotificationLog() {
        ...
    }

```

```java
    @Transactional(readOnly = true)
    public NotificationLog notificationLog(String aNotificationLogId) {
        ...
    }

    @Transactional
    public void publishNotifications() {
        ...
    }
    ...
}

```

Hai phương thức đầu tiên được dùng để truy vấn các thể hiện `NotificationLog` cung cấp cho client dưới dạng tài nguyên RESTful, và phương thức thứ ba được dùng để xuất bản từng thể hiện `Notification` riêng lẻ qua cơ chế tin nhắn. Đội ngũ trước tiên sẽ giải quyết các phương thức truy vấn để lấy các thể hiện `NotificationLog`, sau đó mới chuyển sự chú ý sang phần tương tác với hạ tầng tin nhắn.

Có rất nhiều phần hiện thực mã nguồn thú vị đang chờ đón phía trước.

## Publishing the NotificationLog

Hãy nhớ lại rằng có hai loại log thông báo: current log và archived log. Do đó, giao diện `NotificationService` cung cấp một phương thức truy vấn riêng cho từng loại:

```java
public class NotificationService {
    @Transactional(readOnly = true)
    public NotificationLog currentNotificationLog() {
        EventStore eventStore = EventStore.instance();

        return this.findNotificationLog(
            this.calculateCurrentNotificationLogId(eventStore),
            eventStore);
    }

    @Transactional(readOnly = true)
    public NotificationLog notificationLog(String aNotificationLogId) {
        EventStore eventStore = EventStore.instance();

        return this.findNotificationLog(
            new NotificationLogId(aNotificationLogId),
            eventStore);
    }
    ...
}

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000346_48de86d0bb4006291849a16a580d1d8b5ca05ddf5aeaf72ca955cdb572bfc48e.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000347_4fc094f216ec53b12f670431bbda848466d2641dcebdc0bfc4b105edbba8b696.png)

Về bản chất, cả hai phương thức này đều phải "tìm kiếm" một `NotificationLog`. Điều đó thực chất là việc tìm ra một phân đoạn các thể hiện `DomainEvent` đã được tuần tự hóa trong Event Store, bọc từng sự kiện bằng một `Notification`, và gom tất cả lại thành một `NotificationLog`. Khi một thể hiện `NotificationLog` được tạo ra, nó có thể được biểu diễn dưới dạng một tài nguyên RESTful và gửi về cho client yêu cầu.

Vì current log là một mục tiêu luôn biến đổi, định danh của nó phải được tính toán lại mỗi khi có yêu cầu. Đây là logic tính toán:

```java
public class NotificationService {
    ...
    protected NotificationLogId calculateCurrentNotificationLogId(
        EventStore anEventStore) {

        long count = anEventStore.countStoredEvents();
        long remainder = count % LOG_NOTIFICATION_COUNT;

        if (remainder == 0) {
            remainder = LOG_NOTIFICATION_COUNT;
        }

        long low = count - remainder + 1;
        // đảm bảo tạo ra một giá trị ID hợp lệ ngay cả khi hiện tại
        // chưa có đủ một tập hợp thông báo hoàn chỉnh
        long high = low + LOG_NOTIFICATION_COUNT - 1;

        return new NotificationLogId(low, high);
    }
    ...
}

```

Ngược lại, đối với một archived log, tất cả những gì cần là một `NotificationLogId` để bao bọc dải giá trị cận dưới (low) và cận trên (high) của định danh. Hãy nhớ rằng định danh được mã hóa dưới dạng chuỗi văn bản thể hiện một khoảng giữa giá trị thấp và cao, chẳng hạn như `21,40`. Do đó, constructor cho một định danh đã mã hóa sẽ có dạng như sau:

```java
public class NotificationLogId {
    ...
    public NotificationLogId(String aNotificationLogId) {
        super();
        String[] textIds = aNotificationLogId.split(",");
        this.setLow(Long.parseLong(textIds[0]));
        this.setHigh(Long.parseLong(textIds[1]));
    }
    ...
}

```

Dù là truy vấn cho current log hay archived log, lúc này chúng ta đã có một `NotificationLogId` mô tả chính xác những gì phương thức `findNotificationLog()` cần truy vấn:

```java
public class NotificationService {
    ...
    protected NotificationLog findNotificationLog(
        NotificationLogId aNotificationLogId,
        EventStore anEventStore) {

        List<StoredEvent> storedEvents =
            anEventStore.allStoredEventsBetween(
                aNotificationLogId.low(),
                aNotificationLogId.high());

        long count = anEventStore.countStoredEvents();

        boolean archivedIndicator =
            aNotificationLogId.high() < count;

        NotificationLog notificationLog =
            new NotificationLog(
                aNotificationLogId.encoded(),
                NotificationLogId.encoded(
                    aNotificationLogId.next(LOG_NOTIFICATION_COUNT)),
                NotificationLogId.encoded(
                    aNotificationLogId.previous(LOG_NOTIFICATION_COUNT)),
                this.notificationsFrom(storedEvents),
                archivedIndicator);

        return notificationLog;
    }
    ...
    protected List<Notification> notificationsFrom(
        List<StoredEvent> aStoredEvents) {

        List<Notification> notifications =
            new ArrayList<Notification>(aStoredEvents.size());

        for (StoredEvent storedEvent : aStoredEvents) {
            DomainEvent domainEvent =
                EventStore.toDomainEvent(storedEvent);

            Notification notification =
                new Notification(
                    domainEvent.getClass().getSimpleName(),
                    storedEvent.eventId(),
                    domainEvent.occurredOn(),
                    domainEvent);

            notifications.add(notification);
        }

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000348_147caa3e4c6546f8d2a7aaf537d76e86812b59903e4e19ce7f26b3ddfae05adb.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000349_f1955e6df91518ce2e7d3b1a67d990e6fddb08d941a1918711a9223ab6aff648.png)

```java
        return notifications;
    }
    ...
}

```

Một chi tiết rất thú vị là chúng ta không cần phải lưu trữ cố định bất kỳ thể hiện `Notification` hay toàn bộ bản log nào vào database. Chúng ta hoàn toàn có thể khởi tạo chúng mỗi khi cần thiết. Hiển nhiên, chính vì lý do đó, việc cache các tài nguyên `NotificationLog` ngay tại các điểm tiếp nhận yêu cầu sẽ giúp cải thiện đáng kể hiệu năng và khả năng mở rộng.

Phương thức `findNotificationLog()` sử dụng thành phần `EventStore` để truy vấn các thể hiện `StoredEvent` cần thiết cho một bản log nhất định. Dưới đây là cách `EventStore` tìm kiếm chúng:

```java
package com.saasovation.identityaccess.application.eventStore;
...
public class EventStore ... {
    ...
    public List<StoredEvent> allStoredEventsBetween(
        long aLowStoredEventId,
        long aHighStoredEventId) {

        Query query = this.session().createQuery(
            "from StoredEvent as _obj_ " +
            "where _obj_.eventId between ? and ? " +
            "order by _obj_.eventId");

        query.setParameter(0, aLowStoredEventId);
        query.setParameter(1, aHighStoredEventId);

        List<StoredEvent> storedEvents = query.list();

        return storedEvents;
    }
    ...
}

```

Cuối cùng, tại tầng Web, chúng ta tiến hành xuất bản current log và các archived log:

```java
@Path("/notifications")
public class NotificationResource {
    ...
    @GET
    @Produces({ OvationsMediaType.NAME })
    public Response getCurrentNotificationLog(
        @Context UriInfo aUriInfo) {

```

```java
        NotificationLog currentNotificationLog =
            this.notificationService().currentNotificationLog();

        if (currentNotificationLog == null) {
            throw new WebApplicationException(Response.Status.NOT_FOUND);
        }

        Response response =
            this.currentNotificationLogResponse(
                currentNotificationLog,
                aUriInfo);

        return response;
    }

    @GET
    @Path("{notificationId}")
    @Produces({ OvationsMediaType.ID_OVATION_NAME })
    public Response getNotificationLog(
        @PathParam("notificationId") String aNotificationId,
        @Context UriInfo aUriInfo) {

        NotificationLog notificationLog =
            this.notificationService().notificationLog(aNotificationId);

        if (notificationLog == null) {
            throw new WebApplicationException(Response.Status.NOT_FOUND);
        }

        Response response =
            this.notificationLogResponse(notificationLog, aUriInfo);

        return response;
    }
    ...
}

```

Đội ngũ phát triển hoàn toàn có thể sử dụng một `MessageBodyWriter` để sinh response, nhưng có một vài điểm phức tạp nhỏ cần xử lý nên chúng được gom vào các phương thức dựng response (response builder).

Phần trên đã bao quát các mắt xích trọng yếu dùng để xuất bản cả current log lẫn archived notification log tới các RESTful client.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000350_6e97741faa5f6f15039d0b07fec86f720a9451a70a58e9e2234d0e99b5f805ae.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000351_ced0f267ab7f1eb7c5e5cc0d0700013f25259a02c04a973aaf13743ca9b685a6.png)

## Publishing Message-Based Notifications

`NotificationService` cung cấp một phương thức duy nhất để xuất bản các thể hiện `DomainEvent` qua hạ tầng tin nhắn. Dưới đây là phương thức service đó:

```java
public class NotificationService {
    ...
    @Transactional
    public void publishNotifications() {
        PublishedMessageTracker publishedMessageTracker =
            this.publishedMessageTracker();

        List<Notification> notifications =
            this.listUnpublishedNotifications(
                publishedMessageTracker.mostRecentPublishedMessageId());

        MessageProducer messageProducer = this.messageProducer();

        try {
            for (Notification notification : notifications) {
                this.publish(notification, messageProducer);
            }

            this.trackMostRecentPublishedMessage(
                publishedMessageTracker,
                notifications);
        } finally {
            messageProducer.close();
        }
    }
    ...
}

```

Phương thức `publishNotifications()` trước tiên lấy về đối tượng `PublishedMessageTracker`. Đây là đối tượng lưu trữ bản ghi theo dõi xem những Event nào đã được xuất bản:

```java
package com.saasovation.identityaccess.application.notifications;
...
public class PublishedMessageTracker {
    private long mostRecentPublishedMessageId;
    private long trackerId;
    private String type;
    ...
}

```

Lưu ý rằng lớp này không thuộc về domain model mà thuộc về tầng ứng dụng (application). `trackerId` chỉ là định danh duy nhất của đối tượng này (về bản chất là một Entity — thực thể). Thuộc tính `type` lưu chuỗi `String` mô tả loại topic/channel mà các Event đã được xuất bản tới. Thuộc tính `mostRecentPublishedMessageId` tương ứng với định danh duy nhất của từng `DomainEvent` riêng lẻ đã được tuần tự hóa và lưu thành `StoredEvent`. Do đó, nó nắm giữ giá trị `eventId` của thể hiện `StoredEvent` được xuất bản gần đây nhất. Sau khi toàn bộ các tin nhắn `Notification` mới được gửi đi, phương thức service đảm bảo rằng `PublishedMessageTracker` được lưu lại cùng với định danh của Event vừa mới được xuất bản xong.

Định danh của Event kết hợp cùng thuộc tính `type` cho phép chúng ta xuất bản cùng một tập thông báo tại các thời điểm khác nhau tới nhiều topic/channel tùy ý. Chúng ta chỉ cần tạo một thể hiện mới của `PublishedMessageTracker` với tên của topic/channel đặt làm giá trị `type`, rồi bắt đầu lại từ `StoredEvent` đầu tiên. Trên thực tế, đây là cách mà phương thức `publishedMessageTracker()` hoạt động:

```java
public class NotificationService {
    private static final String EXCHANGE_NAME = "saasovation.identity_access";
    ...
    private PublishedMessageTracker publishedMessageTracker() {
        Query query = this.session().createQuery(
            "from PublishedMessageTracker as _obj_ " +
            "where _obj_.type = ?");

        query.setParameter(0, EXCHANGE_NAME);

        PublishedMessageTracker publishedMessageTracker =
            (PublishedMessageTracker) query.uniqueResult();

        if (publishedMessageTracker == null) {
            publishedMessageTracker =
                new PublishedMessageTracker(EXCHANGE_NAME);
        }

        return publishedMessageTracker;
    }
    ...
}

```

Việc xuất bản đa kênh (multichannel) hiện chưa được hỗ trợ, nhưng có thể dễ dàng bổ sung thêm với một vài bước tái cấu trúc mã nguồn (refactoring).

Tiếp theo, phương thức `listUnpublishedNotifications()` chịu trách nhiệm truy vấn danh sách đã sắp xếp của tất cả các thể hiện `Notification` chưa được xuất bản:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000352_bcbccff962b758c2159f9b997567ec20584ce5799acf6c6b6b692f9da9130c53.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000353_00247b63c5a0fc3332aa963f8436c56a8f8d39354bddb9a55d6fb17f83ababa0.png)

```java
public class NotificationService {
    ...
    protected List<Notification> listUnpublishedNotifications(
        long aMostRecentPublishedMessageId) {

        EventStore eventStore = EventStore.instance();

        List<StoredEvent> storedEvents =
            eventStore.allStoredEventsSince(
                aMostRecentPublishedMessageId);

        List<Notification> notifications =
            this.notificationsFrom(storedEvents);

        return notifications;
    }
    ...
}

```

Trong thực tế, nó đang truy vấn từ `EventStore` các thể hiện `StoredEvent` có giá trị `eventId` lớn hơn giá trị được truyền vào qua tham số `aMostRecentPublishedMessageId`. Các đối tượng trả về từ `EventStore` sẽ được dùng để khởi tạo một tập hợp mới chứa các thể hiện `Notification`.

Bây giờ, quay trở lại phương thức service chính `publishNotifications()`. Với tập hợp các thể hiện `Notification` bao bọc bên ngoài `DomainEvent`, phương thức này lặp qua từng phần tử và chuyển giao cho hàm `publish()`:

```java
        ...
        for (Notification notification : notifications) {
            this.publish(notification, messageProducer);
        }

```

Phương thức xuất bản từng thể hiện `Notification` này thực hiện gửi dữ liệu qua RabbitMQ, nhưng thông qua một thư viện đối tượng rất đơn giản nhằm giúp giao diện của nó mang tính hướng đối tượng hơn:

```java
public class NotificationService {
    ...
    protected void publish(
        Notification aNotification,
        MessageProducer aMessageProducer) {

        MessageParameters messageParameters =
            MessageParameters.durableTextParameters(
                aNotification.type(),
                Long.toString(aNotification.notificationId()),
                aNotification.occurredOn());

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000354_429e4939cc48031a5356e2ee538e57006ff5a94c9fc87bb2af94fe48d3f50617.png)

```java
        String notification =
            NotificationService
                .objectSerializer()
                .serialize(aNotification);

        aMessageProducer.send(notification, messageParameters);
    }
    ...
}

```

Phương thức `publish()` này khởi tạo `MessageParameters` rồi gửi chuỗi JSON đã tuần tự hóa của `DomainEvent` thông qua một `MessageProducer`. 3 `MessageParameters` bao gồm các thuộc tính được chọn lọc để gửi kèm theo phần thân của tin nhắn (message body). Trong số các tham số đặc biệt này có chuỗi định danh loại Event (`type`), mã định danh thông báo dùng làm ID tin nhắn duy nhất (message ID), và dấu thời gian `occurredOn` của Event. Những tham số này cho phép các subscriber nắm bắt được các thông tin quan trọng về từng tin nhắn mà không cần phải bóc tách (parse) nội dung JSON ở phần thân tin nhắn (vốn là Event đã được tuần tự hóa). Và ID tin nhắn duy nhất (định danh của notification) đóng vai trò hỗ trợ việc khử trùng lặp tin nhắn (message de-duplication) — kỹ thuật sẽ được giải thích ở phần sau.

Hãy xem xét thêm một phương thức nữa được dùng để hoàn thiện cơ chế xuất bản:

```java
public class NotificationService {
    ...
    private MessageProducer messageProducer() {
        // tạo exchange nếu chưa tồn tại
        Exchange exchange =
            Exchange.fanOutInstance(
                ConnectionSettings.instance(),
                EXCHANGE_NAME,
                true);

        // tạo một message producer dùng để chuyển tiếp các Event
        MessageProducer messageProducer =
            MessageProducer.instance(exchange);

        return messageProducer;
    }
    ...
}

```

3. Các lớp `Exchange`, `ConnectionSettings`, `MessageProducer`, `MessageParameters` và các lớp khác nằm trong một thư viện đóng vai trò là một lớp trừu tượng (abstraction layer) bọc quanh RabbitMQ. Tôi cung cấp thư viện này — giúp việc sử dụng RabbitMQ trở nên thân thiện và mang tính hướng đối tượng hơn nhiều — kèm theo các đoạn mã nguồn mẫu khác của cuốn sách.